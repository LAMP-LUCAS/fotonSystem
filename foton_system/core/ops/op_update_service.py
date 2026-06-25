from typing import Dict, Any
from foton_system.core.ops.base_op import BaseOp
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort

VALID_SERVICE_FIELDS = [
    'Modalidade', 'Ano', 'Demanda', 'AreaTotal', 'AreaCoberta',
    'AreaDescoberta', 'Detalhes', 'Estilo', 'Ambientes',
    'ValorProposta', 'ValorContrato',
]


class OpUpdateService(BaseOp):
    """
    POP: Update a specific field of a service.
    Validates field name and value, logs audit event.
    """

    def __init__(self, repository: ClientRepositoryPort, actor: str = "System"):
        super().__init__(actor=actor)
        self._repo = repository

    def validate(self, **kwargs) -> Dict[str, Any]:
        client_alias = kwargs.get("client_alias")
        service_alias = kwargs.get("service_alias")
        field = kwargs.get("field")
        value = kwargs.get("value")

        if not client_alias or not isinstance(client_alias, str) or not client_alias.strip():
            raise ValueError("Client alias is required.")
        if not service_alias or not isinstance(service_alias, str) or not service_alias.strip():
            raise ValueError("Service alias is required.")
        if not field or not isinstance(field, str) or not field.strip():
            raise ValueError("Field name is required.")
        if value is None:
            raise ValueError("Value is required.")

        kwargs["client_alias"] = client_alias.strip()
        kwargs["service_alias"] = service_alias.strip()
        kwargs["field"] = field.strip()

        if kwargs["field"] not in VALID_SERVICE_FIELDS:
            raise ValueError(
                f"Campo inválido: {field}. Válidos: {', '.join(VALID_SERVICE_FIELDS)}"
            )

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
        df = self._repo.get_services_dataframe()
        mask = (df['AliasCliente'] == validated_data["client_alias"]) & (df['Alias'] == validated_data["service_alias"])
        df.loc[mask, validated_data["field"]] = validated_data["value"]
        self._repo.save_services(df)
        return {
            "success": True,
            "message": f"Campo '{validated_data['field']}' atualizado com sucesso.",
            "client_alias": validated_data["client_alias"],
            "service_alias": validated_data["service_alias"],
            "field": validated_data["field"],
            "value": validated_data["value"],
        }
