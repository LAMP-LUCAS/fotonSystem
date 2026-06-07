from pathlib import Path
from typing import Optional, Set

from foton_system.modules.shared.infrastructure.config.config import Config


def resolve_client_path(client_name: str, clients_dir: Path, ignored: Optional[Set[str]] = None) -> Path:
    """
    Resolves a client name to a validated directory path.
    Supports exact match and partial/fuzzy matching.
    Raises ValueError if not found or ambiguous.
    """
    if ignored is None:
        ignored = {'.obsidian'}

    if not clients_dir.exists():
        raise ValueError(f"Diretório de clientes não encontrado: {clients_dir}")

    exact = clients_dir / client_name
    if exact.exists() and exact.is_dir():
        return exact

    search = client_name.lower()
    matches = []
    for d in clients_dir.iterdir():
        if d.is_dir() and d.name not in ignored:
            if search in d.name.lower():
                matches.append(d)

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        names = [m.name for m in matches]
        raise ValueError(
            f"Nome de cliente ambíguo '{client_name}'. Encontrados {len(matches)} correspondências: "
            f"{', '.join(names)}. Por favor, seja mais específico."
        )
    else:
        raise ValueError(
            f"Cliente '{client_name}' não encontrado. "
            f"Use 'listar_clientes' para ver os clientes disponíveis."
        )


def list_service_nodes(client_name: str, clients_dir: Path, ignored: Optional[Set[str]] = None) -> list[dict]:
    if ignored is None:
        ignored = set()
    client_path = resolve_client_path(client_name, clients_dir, ignored)
    nodes = []
    for entry in sorted(client_path.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith('_'):
            continue
        if entry.name in ignored:
            continue
        parts = entry.name.split('__')
        depth = len(parts) - 1
        parent = parts[0] if depth >= 1 else None
        nodes.append({
            'name': entry.name,
            'path': entry,
            'depth': depth,
            'parent': parent,
        })
    return nodes


def generate_client_code(name: str, existing_codes: set) -> Optional[str]:
    if not name:
        return None
    parts = name.split()
    if len(parts) > 2:
        base_code = (parts[0][:2] + parts[-1][:2]).upper()
    else:
        base_code = ''.join(filter(str.isalnum, name[:4].upper()))

    code = base_code
    counter = 1
    while code in existing_codes:
        code = f"{base_code}{counter:02d}"
        counter += 1
    return code
