"""Templates padrão de fichas de clientes e serviços."""

CLIENT_TEMPLATE_STR = """## INFO-CLIENTE.md
Aqui tem todas as colunas da tabela de clientes e variáveis extra para personalização

### DADOS DO CLIENTE - PROPOSTA

Dados que serão utilizados nas propostas comerciais:

@dataProposta; 
@numeroProposta; 
@nomeProposta; 
@cidadeProposta; 
@localProposta; 
@geolocalizacaoProposta; 
@nomeCliente; 
@empregoCliente; 
@estadoCivilCliente; 
@cpfCnpjCliente; 
@enderecoCliente; 
"""

SERVICE_TEMPLATE_STR = """## INFO-SERVICO.md

@TEMPLATE; 

### DADOS BÁSICOS

@DataAtual; 

### DADOS DO CLIENTE - CONTRATO

O cliente pode precisar utilizar dados distintos no contrato, portanto abaixo tem os dados para a contratação do serviço:

@nomeContrato; 
@numeroContrato; 
@nomeClienteContrato; 
@estadoCivilClienteContrato; 
@empregoClienteContrato; 
@telefoneClienteContrato; 
@emailClienteContrato; 
@enderecoClienteContrato; 
@cpfCnpjClienteContrato; 

### DADOS DO SERVIÇO

@modalidadeServico; 
@anoProjeto; 
@demandaProposta; 
@areaTotal; 
@areaCoberta; 
@areaDescoberta; 
@detalhesProposta; 
@estiloProjeto; 
@ambientesProjeto; 
@inProposta; 
@lvProposta; 
@anProposta; 
@baProposta; 
@prProposta; 
@inSolucao; 
@valorProposta; 
@valorContrato; 

#### DADOS PARA ESTIMATIVA DE CUSTO - PROPOSTA

@projArqEng; 
@procLegais; 
@ACEqv; 
@execcub; 
@execInfra; 
@execPais; 
@execMob; 
@totalParcial; 
@totalExec; 
@totalinss; 
@totalGeral; 
@ArqEng%; 
@Legais%; 
@precoCUB%; 
@Parcial%; 
@infra%; 
@pais%; 
@mob%; 
@Exec%; 
@inss%; 
"""

__all__ = ["CLIENT_TEMPLATE_STR", "SERVICE_TEMPLATE_STR"]
