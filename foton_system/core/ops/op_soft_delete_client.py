from typing import Dict, Any
from foton_system.core.ops.base_op import BaseOp
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort


class OpSoftDeleteClient(BaseOp):
    """
    POP: Soft delete client — marks a client as DELETADO.
    Creates a smart backup before the operation and logs audit event.
    """

    def __init__(self, repository: ClientRepositoryPort, actor: str = "System"):
        super().__init__(actor=actor)
        self._repo = repository

    def validate(self, **kwargs) -> Dict[str, Any]:
        alias = kwargs.get("alias")
        if not alias or not isinstance(alias, str) or not alias.strip():
            raise ValueError("Client alias is required.")
        kwargs["alias"] = alias.strip()

        df = self._repo.get_clients_dataframe()
        if 'Alias' not in df.columns:
            raise ValueError("Column 'Alias' not found in clients database.")
        if not (df['Alias'] == kwargs["alias"]).any():
            raise ValueError(f"Cliente '{kwargs['alias']}' não encontrado.")

        return kwargs

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        backup = getattr(self._repo, '_create_smart_backup', None)
        if backup:
            backup()
        success = self._repo.soft_delete_client(validated_data["alias"])
        if not success:
            raise RuntimeError(f"Falha ao remover cliente '{validated_data['alias']}'.")
        return {
            "success": True,
            "message": f"Cliente '{validated_data['alias']}' removido com sucesso.",
            "alias": validated_data["alias"],
        }
