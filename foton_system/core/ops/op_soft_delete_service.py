from typing import Dict, Any
from foton_system.core.ops.base_op import BaseOp
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort


class OpSoftDeleteService(BaseOp):
    """
    POP: Soft delete service — marks a service as DELETADO.
    Creates a smart backup before the operation and logs audit event.
    """

    def __init__(self, repository: ClientRepositoryPort, actor: str = "System"):
        super().__init__(actor=actor)
        self._repo = repository

    def validate(self, **kwargs) -> Dict[str, Any]:
        client_alias = kwargs.get("client_alias")
        service_alias = kwargs.get("service_alias")
        if not client_alias or not isinstance(client_alias, str) or not client_alias.strip():
            raise ValueError("Client alias is required.")
        if not service_alias or not isinstance(service_alias, str) or not service_alias.strip():
            raise ValueError("Service alias is required.")
        kwargs["client_alias"] = client_alias.strip()
        kwargs["service_alias"] = service_alias.strip()

        df = self._repo.get_services_dataframe()
        if 'AliasCliente' not in df.columns or 'Alias' not in df.columns:
            raise ValueError("Required columns not found in services database.")
        mask = (df['AliasCliente'] == kwargs["client_alias"]) & (df['Alias'] == kwargs["service_alias"])
        if not mask.any():
            raise ValueError(
                f"Serviço '{kwargs['client_alias']}/{kwargs['service_alias']}' não encontrado."
            )

        return kwargs

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        backup = getattr(self._repo, '_create_smart_backup', None)
        if backup:
            backup()
        success = self._repo.soft_delete_service(
            validated_data["client_alias"], validated_data["service_alias"]
        )
        if not success:
            raise RuntimeError(
                f"Falha ao remover serviço '{validated_data['client_alias']}/{validated_data['service_alias']}'."
            )
        return {
            "success": True,
            "message": f"Serviço '{validated_data['client_alias']}/{validated_data['service_alias']}' removido com sucesso.",
            "client_alias": validated_data["client_alias"],
            "service_alias": validated_data["service_alias"],
        }
