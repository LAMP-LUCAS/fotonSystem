from typing import Dict, Any
from foton_system.core.ops.base_op import BaseOp
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort


class OpRestoreClient(BaseOp):
    """
    POP: Restore a previously soft-deleted client.
    Logs audit event on completion.
    """

    def __init__(self, repository: ClientRepositoryPort, actor: str = "System"):
        super().__init__(actor=actor)
        self._repo = repository

    def validate(self, **kwargs) -> Dict[str, Any]:
        alias = kwargs.get("alias")
        if not alias or not isinstance(alias, str) or not alias.strip():
            raise ValueError("Client alias is required.")
        kwargs["alias"] = alias.strip()

        deleted = self._repo.get_deleted_clients()
        if not any(c['Alias'] == kwargs["alias"] for c in deleted):
            raise ValueError(
                f"Cliente '{kwargs['alias']}' não está deletado ou não existe."
            )

        return kwargs

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        success = self._repo.restore_client(validated_data["alias"])
        if not success:
            raise RuntimeError(f"Falha ao restaurar cliente '{validated_data['alias']}'.")
        return {
            "success": True,
            "message": f"Cliente '{validated_data['alias']}' restaurado com sucesso.",
            "alias": validated_data["alias"],
        }
