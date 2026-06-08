#!/usr/bin/env python3
"""
Migration Script — Client Folder Structure Reorganization.

Phases:
  1. Backup (copy all CLIENTES/ to timestamped backup)
  2. Scan & Report (dry-run)
  3. Merge confirmed duplicates by NIF or similarity
  4. Rename folders to UPPER_SNAKE_CASE
  5. Create functional folders ({DOC}, {ADM}, {OP} + phases)
  6. Flatten sub-service hierarchy using __ separator
  7. Normalize INFO files to canonical names

Usage:
    python migrate_client_structure.py              # interactive
    python migrate_client_structure.py --dry-run     # report only
    python migrate_client_structure.py --force       # skip confirmations
    python migrate_client_structure.py --rollback    # restore from backup
"""

import argparse
import shutil
import sys
import json
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher


# ---------------------------------------------------------------------------
# CONFIG — Loaded from Foton settings.json
# ---------------------------------------------------------------------------

def load_config():
    """Load foton config from settings.json."""
    # Try standard locations
    candidates = [
        Path(__file__).resolve().parents[1] / "foton_system" / "config" / "settings.json",
        Path.cwd() / "foton_system" / "config" / "settings.json",
        Path.home() / "AppData" / "Local" / "FotonSystem" / "config" / "settings.json",
    ]
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f), path.parent
    # Fallback defaults
    return {
        "caminho_pastaClientes": str(Path.cwd() / "CLIENTES"),
        "caminho_baseDados": str(Path.cwd() / "BASE"),
        "ignored_folders": ["DOC", "ARQ", "HID", "ELE", "STR", "PL", "EVT"],
        "folder_conventions": {
            "doc": "00_DOC",
            "adm": "01_ADM",
            "op": "02_OPERACAO",
            "op_phases": ["EP", "AP", "EXE", "REL"],
        },
    }, Path.cwd()


# ---------------------------------------------------------------------------
# FILE OPS
# ---------------------------------------------------------------------------

def ignore_patterns():
    """Returns a shutil.ignore_patterns callable for common temp files."""
    return shutil.ignore_patterns(
        "*.bak", "*.tmp", "*.swp", "~*", "__pycache__", ".obsidian"
    )


def backup_clients(clients_dir: Path, backup_dir: Path) -> int:
    """Copy entire CLIENTES/ directory to backup. Returns file count."""
    if not clients_dir.exists():
        print(f"[SKIP] Client dir does not exist: {clients_dir}")
        return 0
    backup_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in clients_dir.iterdir():
        if item.is_dir():
            dest = backup_dir / item.name
            shutil.copytree(item, dest, ignore=ignore_patterns())
            count += sum(1 for _ in dest.rglob("*"))
    return count


def restore_backup(clients_dir: Path, backup_dir: Path) -> int:
    """Restore CLIENTES/ from backup."""
    if not backup_dir.exists():
        print(f"[ERROR] Backup not found: {backup_dir}")
        return 0
    if clients_dir.exists():
        shutil.rmtree(clients_dir)
    clients_dir.mkdir(parents=True)
    count = 0
    for item in backup_dir.iterdir():
        if item.is_dir():
            dest = clients_dir / item.name
            shutil.copytree(item, dest)
            count += 1
    return count


# ---------------------------------------------------------------------------
# SCANNING
# ---------------------------------------------------------------------------

def scan_client_folders(clients_dir: Path, ignored: list) -> list[dict]:
    """Scan CLIENTES/ and return metadata for each client folder."""
    clients = []
    if not clients_dir.exists():
        return clients
    for d in sorted(clients_dir.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name in ignored:
            continue
        services = []
        for s in sorted(d.iterdir()):
            if s.is_dir() and not s.name.startswith(".") and s.name not in ignored:
                services.append({
                    "name": s.name,
                    "path": s,
                    "has_info": bool(list(s.glob("*INFO*.md"))),
                    "has_finance": (s / "FINANCEIRO.csv").exists(),
                    "subs": [x.name for x in s.iterdir() if x.is_dir()],
                })
        # Also check for service subdirs with __ already
        flat_sub_services = [s for s in services if "__" in s["name"]]
        clients.append({
            "name": d.name,
            "path": d,
            "has_info": bool(list(d.glob("*INFO*.md"))),
            "has_finance": (d / "FINANCEIRO.csv").exists(),
            "services": services,
            "flat_sub_services": flat_sub_services,
        })
    return clients


# ---------------------------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------------------------

def normalize_name(name: str) -> str:
    """Convert to UPPER_SNAKE_CASE without accents or hyphens."""
    import unicodedata, re
    if not name:
        return ""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    upper = ascii_only.upper()
    no_dash = re.sub(r"[-\s]+", "_", upper)
    clean = re.sub(r"[^A-Z0-9_]", "", no_dash)
    clean = re.sub(r"_+", "_", clean)
    return clean.strip("_")


# ---------------------------------------------------------------------------
# DUPLICATE DETECTION
# ---------------------------------------------------------------------------

def find_duplicates(clients: list[dict]) -> list[tuple]:
    """Find potential duplicate clients by name similarity."""
    pairs = []
    for i, a in enumerate(clients):
        for b in clients[i + 1:]:
            ratio = SequenceMatcher(None, a["name"], b["name"]).ratio()
            if ratio > 0.7:
                pairs.append((a, b, ratio))
    return pairs


# ---------------------------------------------------------------------------
# RENAME
# ---------------------------------------------------------------------------

def rename_to_normalized(clients: list[dict], dry_run: bool) -> list[dict]:
    """Rename client folders to UPPER_SNAKE_CASE. Returns renamed list."""
    renamed = []
    for c in clients:
        new_name = normalize_name(c["name"])
        if new_name != c["name"]:
            if not dry_run:
                (c["path"]).rename(c["path"].parent / new_name)
            renamed.append({"old": c["name"], "new": new_name, "path": c["path"].parent / new_name})
        # Rename services too
        for s in c["services"]:
            new_svc = normalize_name(s["name"])
            if new_svc != s["name"] and not dry_run:
                (s["path"]).rename(s["path"].parent / new_svc)
    return renamed


# ---------------------------------------------------------------------------
# FUNCTIONAL FOLDERS
# ---------------------------------------------------------------------------

def ensure_functional_folders(clients: list[dict], fc: dict, dry_run: bool) -> list[dict]:
    """Create {DOC}/{ADM}/{OP} + phases in each client and service folder."""
    created = []
    doc_name = fc.get("doc", "00_DOC")
    adm_name = fc.get("adm", "01_ADM")
    op_name = fc.get("op", "02_OPERACAO")
    phases = fc.get("op_phases", ["EP", "AP", "EXE", "REL"])

    def _ensure(parent: Path, label: str):
        if not dry_run:
            (parent / doc_name).mkdir(exist_ok=True)
            (parent / adm_name).mkdir(exist_ok=True)
            op = parent / op_name
            op.mkdir(exist_ok=True)
            for p in phases:
                (op / p).mkdir(exist_ok=True)
        created.append(f"{label}: {doc_name}/{adm_name}/{op_name}")

    for c in clients:
        _ensure(c["path"], c["name"])
        for s in c.get("services", []):
            _ensure(s["path"], f"{c['name']}/{s['name']}")
    return created


# ---------------------------------------------------------------------------
# FLATTEN SUB-SERVICES
# ---------------------------------------------------------------------------

def flatten_sub_services(clients: list[dict], dry_run: bool) -> list[dict]:
    """Move deep sub-service folders up to client root using __ separator."""
    flattened = []
    for c in clients:
        for s in c["services"]:
            subs = [x for x in s["path"].iterdir() if x.is_dir()]
            sub_names = {x.name for x in subs}
            functional = {"00_DOC", "01_ADM", "02_OPERACAO", "DOC", "ARQ", "HID", "ELE", "STR", "PL", "EVT", "EP", "AP", "EXE", "REL"}
            real_subs = [x for x in subs if x.name not in functional and "__" not in s["name"]]
            for sub in real_subs:
                new_name = f"{s['name']}__{sub.name}"
                dest = c["path"] / new_name
                if not dry_run:
                    sub.rename(dest)
                flattened.append({"parent": s["name"], "old": sub.name, "new": new_name})
    return flattened


# ---------------------------------------------------------------------------
# NORMALIZE INFO FILES
# ---------------------------------------------------------------------------

def normalize_info_files(clients: list[dict], dry_run: bool) -> list[str]:
    """Rename *INFO*.md to canonical INFO-CLIENTE.md or INFO-SERVICO.md."""
    renamed = []
    for c in clients:
        # Client-level INFO
        for f in c["path"].glob("*INFO*.md"):
            if f.name.upper() not in ("INFO-CLIENTE.MD",):
                dest = c["path"] / "INFO-CLIENTE.md"
                if not dest.exists() and not dry_run:
                    f.rename(dest)
                    renamed.append(f"{c['name']}: {f.name} -> INFO-CLIENTE.md")
        # Service-level INFO
        for s in c["services"]:
            for f in s["path"].glob("*INFO*.md"):
                if f.name.upper() not in ("INFO-SERVICO.MD",):
                    dest = s["path"] / "INFO-SERVICO.md"
                    if not dest.exists() and not dry_run:
                        f.rename(dest)
                        renamed.append(f"{c['name']}/{s['name']}: {f.name} -> INFO-SERVICO.md")
    return renamed


# ---------------------------------------------------------------------------
# MOVE FINANCEIRO.CSV
# ---------------------------------------------------------------------------

def migrate_finance_csv(clients: list[dict], fc: dict, dry_run: bool) -> list[str]:
    """Move root FINANCEIRO.csv to {ADM}/FINANCEIRO.csv if not already there."""
    adm_name = fc.get("adm", "01_ADM")
    moved = []
    for c in clients:
        root_csv = c["path"] / "FINANCEIRO.csv"
        adm_csv = c["path"] / adm_name / "FINANCEIRO.csv"
        if root_csv.exists() and not adm_csv.exists() and not dry_run:
            (c["path"] / adm_name).mkdir(exist_ok=True)
            shutil.move(str(root_csv), str(adm_csv))
            moved.append(c["name"])
    return moved


# ---------------------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------------------

def print_report(clients: list[dict], duplicates: list[tuple],
                 renamed: list[dict], folders: list[dict],
                 flat: list[dict], infos: list[str], finance: list[str]):
    """Print a comprehensive migration report."""
    print("\n" + "=" * 60)
    print("  CLIENT STRUCTURE MIGRATION REPORT")
    print("=" * 60)

    print(f"\n📁 Total clients found: {len(clients)}")
    for c in clients:
        svc_count = len(c["services"])
        info_mark = "✅" if c["has_info"] else "❌"
        fin_mark = "💰" if c["has_finance"] else "⬜"
        flat_svc = f" ({len(c['flat_sub_services'])} flat)" if c["flat_sub_services"] else ""
        print(f"  {info_mark} {c['name']} ({svc_count} services{flat_svc}) {fin_mark}")

    if duplicates:
        print(f"\n⚠️  Potential duplicates ({len(duplicates)}):")
        for a, b, r in duplicates:
            print(f"  {a['name']} <-> {b['name']} (similarity: {r:.0%})")

    if renamed:
        print(f"\n🏷️  Renamed to UPPER_SNAKE_CASE ({len(renamed)}):")
        for r in renamed:
            print(f"  {r['old']} → {r['new']}")

    if folders:
        print(f"\n📂 Functional folders created: {len(folders)}")

    if flat:
        print(f"\n🔀 Sub-services flattened ({len(flat)}):")
        for f in flat:
            print(f"  {f['parent']}/{f['old']} → {f['new']}")

    if infos:
        print(f"\n📄 INFO files normalized ({len(infos)}):")
        for i in infos[:10]:
            print(f"  {i}")
        if len(infos) > 10:
            print(f"  ... and {len(infos) - 10} more")

    if finance:
        print(f"\n💰 FINANCEIRO.csv moved to {{ADM}}/ ({len(finance)} clients):")
        for f in finance:
            print(f"  {f}")

    print("\n" + "=" * 60)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Migrate client folder structure to new conventions.")
    parser.add_argument("--dry-run", action="store_true", help="Scan and report without making changes.")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts.")
    parser.add_argument("--rollback", metavar="BACKUP_DIR", help="Restore from a backup directory.")
    parser.add_argument("--backup-dir", help="Custom backup directory (default: CLIENTES_backup_<timestamp>).")
    args = parser.parse_args()

    # Load config
    settings, config_dir = load_config()
    clients_dir = Path(settings.get("caminho_pastaClientes", str(Path.cwd() / "CLIENTES")))
    ignored = settings.get("ignored_folders", []) + [".obsidian"]
    fc = settings.get("folder_conventions", {
        "doc": "00_DOC", "adm": "01_ADM", "op": "02_OPERACAO",
        "op_phases": ["EP", "AP", "EXE", "REL"],
    })

    # ── ROLLBACK ──
    if args.rollback:
        backup_path = Path(args.rollback)
        if not backup_path.exists():
            print(f"[ERROR] Backup directory not found: {backup_path}")
            sys.exit(1)
        count = restore_backup(clients_dir, backup_path)
        print(f"✅ Restored {count} clients from {backup_path}")
        return

    # ── BACKUP ──
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(args.backup_dir) if args.backup_dir else clients_dir.parent / f"CLIENTES_backup_{timestamp}"
    if not args.dry_run:
        print(f"📦 Creating backup at: {backup_dir}")
        file_count = backup_clients(clients_dir, backup_dir)
        print(f"   {file_count} files backed up.")
    else:
        print("🏃 Dry-run mode — no changes will be made.\n")

    # ── SCAN ──
    print("🔍 Scanning client folders...")
    clients = scan_client_folders(clients_dir, ignored)
    duplicates = find_duplicates(clients)
    renamed = rename_to_normalized(clients, dry_run=args.dry_run)
    folders = ensure_functional_folders(clients, fc, dry_run=args.dry_run)
    flat = flatten_sub_services(clients, dry_run=args.dry_run)
    infos = normalize_info_files(clients, dry_run=args.dry_run)
    finance = migrate_finance_csv(clients, fc, dry_run=args.dry_run)

    # ── REPORT ──
    print_report(clients, duplicates, renamed, folders, flat, infos, finance)

    # ── CONFIRM ──
    if not args.dry_run and not args.force:
        answer = input("\n❓ Apply these changes? (yes/no): ").strip().lower()
        if answer not in ("yes", "y"):
            print("⏹  Migration cancelled. No changes applied.")
            # Offer rollback info
            if backup_dir.exists():
                print(f"ℹ️  Backup available at: {backup_dir}")
                print(f"   To restore: python migrate_client_structure.py --rollback {backup_dir}")
            return

    if args.dry_run:
        print("\n✅ Dry-run complete. Run without --dry-run to apply changes.")
    else:
        print(f"\n✅ Migration complete! Backup at: {backup_dir}")
        print(f"   To rollback: python migrate_client_structure.py --rollback {backup_dir}")


if __name__ == "__main__":
    main()
