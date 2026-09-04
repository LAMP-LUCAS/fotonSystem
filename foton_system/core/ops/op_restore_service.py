from typing import Dict, Any
from foton_system.core.ops.base_op import BaseOp
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort


class OpRestoreService(BaseOp):
    """
    POP: Restore a previously soft-deleted service.
    Logs audit event on completion.
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

        deleted = self._repo.get_deleted_services()
        if not any(
            s['AliasCliente'] == kwargs["client_alias"] and s['Alias'] == kwargs["service_alias"]
            for s in deleted
        ):
            raise ValueError(
                f"Serviço '{kwargs['client_alias']}/{kwargs['service_alias']}' não está deletado ou não existe."
            )

        return kwargs

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        success = self._repo.restore_service(
            validated_data["client_alias"], validated_data["service_alias"]
        )
        if not success:
            raise RuntimeError(
                f"Falha ao restaurar serviço '{validated_data['client_alias']}/{validated_data['service_alias']}'."
            )
        return {
            "success": True,
            "message": f"Serviço '{validated_data['client_alias']}/{validated_data['service_alias']}' restaurado com sucesso.",
            "client_alias": validated_data["client_alias"],
            "service_alias": validated_data["service_alias"],
        }
