from typing import Dict, Any, Optional
from pathlib import Path

from foton_system.core.ops.base_op import BaseOp
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.clients.application.use_cases import client_query, client_crud

VALID_OPERATIONS = {"append", "replace", "remove", "field"}


class OpUpdateClientInfo(BaseOp):
    """
    POP: Update a client's INFO file (Center of Truth).

    Supports 4 operations:
      - append:  append content to a Markdown section
      - replace: replace entire section content
      - remove:  remove a section entirely
      - field:   update a @campo value via regex

    Creates a .bak backup before modification and logs an audit event.
    """

    def __init__(self, config: Optional[Config] = None, actor: str = "System"):
        super().__init__(actor=actor)
        self._config = config or Config()

    def validate(self, **kwargs) -> Dict[str, Any]:
        client_name = kwargs.get("client_name")
        if not client_name or not isinstance(client_name, str) or not client_name.strip():
            raise ValueError("Client name is required.")
        kwargs["client_name"] = client_name.strip()

        section = kwargs.get("section")
        if not section or not isinstance(section, str) or not section.strip():
            raise ValueError("Section is required.")
        kwargs["section"] = section.strip()

        operacao = kwargs.get("operacao", "append")
        if operacao not in VALID_OPERATIONS:
            raise ValueError(
                f"Operação inválida: {operacao}. "
                f"Válidas: {', '.join(sorted(VALID_OPERATIONS))}."
            )
        kwargs["operacao"] = operacao

        if operacao == "field":
            campo = kwargs.get("campo", "")
            if not campo or not isinstance(campo, str) or not campo.strip():
                raise ValueError("Campo is required for 'field' operation.")
            kwargs["campo"] = campo.strip()

        content = kwargs.get("content", "")
        if not isinstance(content, str):
            raise ValueError("Content must be a string.")

        return kwargs

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        client_name = validated_data["client_name"]
        section = validated_data["section"]
        content = validated_data.get("content", "")
        operacao = validated_data["operacao"]
        campo = validated_data.get("campo", "")

        ignored = set(self._config.ignored_folders)
        client_path = client_query.resolve_client_path(
            client_name, self._config.base_pasta_clientes, ignored
        )

        backup_name = client_crud.update_client_info_file(
            client_path, section, content, operacao=operacao, campo=campo
        )

        return {
            "success": True,
            "message": f"Ficha do cliente '{client_name}' atualizada.",
            "backup": backup_name,
            "client": client_name,
            "operacao": operacao,
        }