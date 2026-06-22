"""Conformance checker for client folder/file patterns.

Detects:
- Folder names with spaces or invalid characters
- Missing INFO files (no file matching the configured pattern)
- INFO files with names outside the configured pattern
- Duplicate INFO files in the same folder
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_ACCEPTED_STATE_FILE = ".conformance_accepted.json"


@dataclass
class ConformanceItem:
    item_id: str
    tipo: str  # 'folder_name' | 'missing_info' | 'pattern_mismatch' | 'duplicate_info'
    severity: str  # 'error' | 'warning'
    description: str
    path: Path
    suggested_fix: str = ""
    details: dict[str, Any] = field(default_factory=dict)


class ClientConformanceChecker:
    """Audits client folders for naming and structure conformance."""

    def __init__(self, config: Any):
        self._config = config
        self._base_path = config.base_pasta_clientes
        self._accepted: list[dict] = []
        self._load_accepted()

    # ------------------------------------------------------------------
    # Persistence of accepted states
    # ------------------------------------------------------------------

    def _accepted_path(self) -> Path:
        return self._base_path / _ACCEPTED_STATE_FILE

    def _load_accepted(self):
        path = self._accepted_path()
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    self._accepted = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load accepted state: {e}")
                self._accepted = []

    def _save_accepted(self):
        path = self._accepted_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._accepted, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save accepted state: {e}")

    def _is_accepted(self, item: ConformanceItem) -> bool:
        return any(
            a.get("item_id") == item.item_id and a.get("tipo") == item.tipo
            for a in self._accepted
        )

    # ------------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------------

    def _check_folder_name(self, folder: Path) -> Optional[ConformanceItem]:
        """Verifica se o nome da pasta contém caracteres inválidos."""
        name = folder.name
        invalid = set(' !@#$%^&*()+={}[]|\\:;"\'<>,?/~`')
        found = [c for c in name if c in invalid]
        if found:
            fixed_name = "".join("_" if c in invalid else c for c in name)
            return ConformanceItem(
                item_id=f"folder_name:{folder.relative_to(self._base_path)}",
                tipo="folder_name",
                severity="warning",
                description=f"Folder name '{name}' contains invalid characters: {set(found)}",
                path=folder,
                suggested_fix=f"Rename to '{fixed_name}'",
                details={"original": name, "suggested": fixed_name},
            )
        return None

    def _check_info_pattern(self, folder: Path, tipo: str) -> Optional[ConformanceItem]:
        """Verifica se o folder tem um INFO file que corresponde ao pattern."""
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager

        glob_pattern = PathManager.get_info_glob(tipo)
        matching = list(folder.glob(glob_pattern))
        all_info = list(folder.glob("*INFO*.md"))

        if not all_info:
            resolver = PathManager.get_info_pattern(tipo)
            kwargs = {"versao": "00", "revisao": "00", "data": str(date.today())}
            if tipo == "cliente":
                kwargs.setdefault("codCliente", folder.name.upper()[:8])
                kwargs.setdefault("nomeCliente", folder.name.upper())
                kwargs.setdefault("aliasCliente", folder.name)
            else:
                kwargs.setdefault("codServico", f"{folder.parent.name[:3]}{folder.name[:3]}01".upper())
                kwargs.setdefault("aliasServico", folder.name)
            # Fill any remaining obligatory placeholders with defaults
            for ph in resolver.placeholders:
                kwargs.setdefault(ph, f"__{ph}__")
            suggested = resolver.resolve(**kwargs)
            return ConformanceItem(
                item_id=f"missing_info:{folder.relative_to(self._base_path)}",
                tipo="missing_info",
                severity="error",
                description=f"No INFO file found in '{folder.name}'",
                path=folder,
                suggested_fix=f"Create {suggested}",
                details={"tipo": tipo},
            )

        legacy = [f for f in all_info if f.name.upper() in ("INFO-CLIENTE.MD", "INFO-SERVICO.MD")]
        if legacy and not matching:
            from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
            resolver = PathManager.get_info_pattern(tipo)
            # Try to read @CodCliente/@CodServico
            cod = ""
            try:
                for line in legacy[0].read_text(encoding="utf-8").splitlines():
                    key = "@codcliente" if tipo == "cliente" else "@codservico"
                    if line.strip().lower().startswith(key):
                        cod = line.split(";", 1)[-1].strip()
            except Exception:
                pass
            kwargs = {"versao": "00", "revisao": "00", "data": str(date.today())}
            if tipo == "cliente":
                kwargs["codCliente"] = cod or folder.name.upper()[:8]
                kwargs["nomeCliente"] = folder.name.upper()
                kwargs["aliasCliente"] = folder.name
            else:
                kwargs["codServico"] = cod or f"{folder.parent.name[:3]}{folder.name[:3]}01".upper()
                kwargs["aliasServico"] = folder.name
            new_name = resolver.resolve(**kwargs)
            return ConformanceItem(
                item_id=f"pattern_mismatch:{legacy[0].relative_to(self._base_path)}",
                tipo="pattern_mismatch",
                severity="warning",
                description=f"'{legacy[0].name}' does not match pattern '{resolver.pattern}'",
                path=legacy[0],
                suggested_fix=f"Rename to '{new_name}'",
                details={"old_name": legacy[0].name, "new_name": new_name},
            )

        if len(matching) > 1:
            return ConformanceItem(
                item_id=f"duplicate_info:{folder.relative_to(self._base_path)}",
                tipo="duplicate_info",
                severity="warning",
                description=f"Multiple INFO files matching pattern in '{folder.name}': {[f.name for f in matching]}",
                path=folder,
                details={"files": [f.name for f in matching]},
            )

        return None

    def check(self) -> list[ConformanceItem]:
        """Executa todas as verificações e retorna itens não conformes."""
        items: list[ConformanceItem] = []

        if not self._base_path.exists():
            logger.warning(f"Base path does not exist: {self._base_path}")
            return items

        for client_dir in sorted(self._base_path.iterdir()):
            if not client_dir.is_dir():
                continue

            # Client folder name check
            item = self._check_folder_name(client_dir)
            if item and not self._is_accepted(item):
                items.append(item)

            # Client INFO file check
            item = self._check_info_pattern(client_dir, "cliente")
            if item and not self._is_accepted(item):
                items.append(item)

            # Service folders
            for svc_dir in sorted(client_dir.iterdir()):
                if not svc_dir.is_dir():
                    continue
                # Skip system folders
                if svc_dir.name in self._config.ignored_folders if hasattr(self._config, 'ignored_folders') else svc_dir.name.startswith("0"):
                    continue

                # Service folder name check
                item = self._check_folder_name(svc_dir)
                if item and not self._is_accepted(item):
                    items.append(item)

                # Service INFO file check
                item = self._check_info_pattern(svc_dir, "servico")
                if item and not self._is_accepted(item):
                    items.append(item)

        return items

    def auto_fix(self, item: ConformanceItem) -> bool:
        """Aplica a correção sugerida para o item."""
        try:
            if item.tipo == "pattern_mismatch":
                new_name = item.details.get("new_name", "")
                if new_name:
                    dest = item.path.parent / new_name
                    if not dest.exists():
                        item.path.rename(dest)
                        logger.info(f"Fixed: {item.path.name} -> {new_name}")
                        return True
                    else:
                        logger.warning(f"Cannot fix: {new_name} already exists")
                        return False
            elif item.tipo == "folder_name":
                fixed_name = item.details.get("suggested", "")
                if fixed_name:
                    dest = item.path.parent / fixed_name
                    if not dest.exists():
                        item.path.rename(dest)
                        logger.info(f"Fixed: folder renamed to '{fixed_name}'")
                        return True
            elif item.tipo == "missing_info":
                from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository
                from foton_system.modules.clients.application.use_cases.client_crud import export_client_data, export_service_data
                tipo = item.details.get("tipo", "")
                folder = item.path
                repo = ExcelClientRepository(config=self._config)
                if tipo == "cliente":
                    export_client_data(repo, self._config, target_alias=folder.name)
                else:
                    export_service_data(repo, self._config, target_client_alias=folder.parent.name, target_service_alias=folder.name)
                logger.info(f"Fixed: created INFO file in '{folder.name}'")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to fix {item.item_id}: {e}")
            return False

    def accept_state(self, item: ConformanceItem) -> bool:
        """Aceita o estado atual e não o reporta novamente."""
        self._accepted.append({
            "item_id": item.item_id,
            "tipo": item.tipo,
            "description": item.description,
        })
        self._save_accepted()
        return True
