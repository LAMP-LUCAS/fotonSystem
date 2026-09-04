#!/usr/bin/env python3
"""Migrate INFO files from legacy naming to configurable pattern.

Usage:
    python scripts/migrate_info_to_pattern.py          # dry-run (default)
    python scripts/migrate_info_to_pattern.py --apply   # rename with .bak
    python scripts/migrate_info_to_pattern.py --rollback # restore from .bak
"""

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path


BAK_MAPPING_FILE = "migrate_info_to_pattern.bak.json"


def _get_client_code(info_path: Path) -> str:
    """Tenta ler @CodCliente do INFO file; fallback para nome da pasta."""
    try:
        for line in info_path.read_text(encoding="utf-8").splitlines():
            if line.strip().lower().startswith("@codcliente"):
                return line.split(";", 1)[-1].strip()
    except Exception:
        pass
    return info_path.parent.name.upper()[:8]


def _get_service_code(info_path: Path, client_folder: Path) -> str:
    """Tenta ler @CodServico; fallback gerado do alias."""
    try:
        for line in info_path.read_text(encoding="utf-8").splitlines():
            if line.strip().lower().startswith("@codservico"):
                return line.split(";", 1)[-1].strip()
    except Exception:
        pass
    alias = info_path.parent.name
    client_alias = client_folder.name
    base = (client_alias[:3] + alias[:3]).upper()
    base = "".join(filter(str.isalnum, base))
    return f"{base}01"


def _new_name(info_path: Path, tipo: str, client_folder: Path) -> str:
    """Gera o novo nome usando o pattern configurado."""
    from foton_system.modules.shared.infrastructure.services.path_manager import PathManager

    alias = info_path.parent.name
    if tipo == "cliente":
        cod = _get_client_code(info_path)
        resolver = PathManager.get_info_pattern("cliente")
        return resolver.resolve(
            codCliente=cod,
            nomeCliente=alias.upper(),
            aliasCliente=alias,
            versao="00",
            revisao="00",
            data=str(date.today()),
        )
    else:
        cod = _get_service_code(info_path, client_folder)
        resolver = PathManager.get_info_pattern("servico")
        return resolver.resolve(
            codServico=cod,
            aliasServico=alias,
            versao="00",
            revisao="00",
            data=str(date.today()),
        )


def _collect_legacy(base_path: Path):
    """Encontra todos os INFO-CLIENTE.md e INFO-SERVICO.md legacy."""
    found = []
    for client_dir in base_path.iterdir():
        if not client_dir.is_dir():
            continue
        # Client-level
        client_info = client_dir / "INFO-CLIENTE.md"
        if client_info.exists():
            found.append(("cliente", client_info, client_dir))
        # Service-level
        for sub in client_dir.iterdir():
            if not sub.is_dir():
                continue
            svc_info = sub / "INFO-SERVICO.md"
            if svc_info.exists():
                found.append(("servico", svc_info, client_dir))
    return found


def _load_mapping(base_path: Path) -> list[dict]:
    mapping_file = base_path / BAK_MAPPING_FILE
    if not mapping_file.exists():
        print(f"[ERROR] Backup mapping not found: {mapping_file}")
        sys.exit(1)
    with open(mapping_file, encoding="utf-8") as f:
        return json.load(f)


def do_dry_run(base_path: Path):
    print("=== DRY RUN — No files will be changed ===\n")
    found = _collect_legacy(base_path)
    if not found:
        print("No legacy INFO files found.")
        return

    for tipo, info_path, client_folder in found:
        novo = _new_name(info_path, tipo, client_folder)
        print(f"  RENAME: {info_path.relative_to(base_path)}")
        print(f"       -> {info_path.parent.name}/{novo}")
    print(f"\nTotal: {len(found)} file(s) to rename.")


def do_apply(base_path: Path):
    mapping = []
    found = _collect_legacy(base_path)
    if not found:
        print("No legacy INFO files found.")
        return

    for tipo, info_path, client_folder in found:
        novo = _new_name(info_path, tipo, client_folder)
        dest = info_path.parent / novo
        if dest.exists():
            print(f"  [SKIP] {dest.name} already exists in {info_path.parent.name}")
            continue
        print(f"  RENAME: {info_path.relative_to(base_path)}")
        print(f"       -> {info_path.parent.name}/{novo}")
        backup_parent = info_path.parent / ".bak_migrate_info"
        backup_parent.mkdir(exist_ok=True)
        shutil.copy2(info_path, backup_parent / info_path.name)
        info_path.rename(dest)
        mapping.append({
            "old": str(info_path.relative_to(base_path)),
            "new": str(dest.relative_to(base_path)),
            "backup": str(backup_parent / info_path.name),
        })

    mapping_file = base_path / BAK_MAPPING_FILE
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] {len(found)} file(s) renamed. Mapping saved to {BAK_MAPPING_FILE}")


def do_rollback(base_path: Path):
    mapping = _load_mapping(base_path)
    restored = 0
    for entry in mapping:
        bak = Path(entry["backup"])
        dest = base_path / entry["old"]
        if bak.exists():
            bak.rename(dest)
            restored += 1
            print(f"  RESTORED: {entry['old']}")
        else:
            print(f"  [WARN] Backup not found: {bak}")

    mapping_file = base_path / BAK_MAPPING_FILE
    if mapping_file.exists():
        mapping_file.unlink()
    print(f"\n[OK] {restored}/{len(mapping)} file(s) restored.")


def main():
    parser = argparse.ArgumentParser(description="Migrate INFO files to configurable pattern")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="Execute renaming with .bak backup")
    group.add_argument("--rollback", action="store_true", help="Restore from .bak backup")
    args = parser.parse_args()

    from foton_system.modules.shared.infrastructure.config.config import Config
    config = Config()
    base_path = config.base_pasta_clientes

    if args.rollback:
        do_rollback(base_path)
    elif args.apply:
        do_apply(base_path)
    else:
        do_dry_run(base_path)


if __name__ == "__main__":
    main()
