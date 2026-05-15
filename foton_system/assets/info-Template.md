# TEMPLATE DE VARIÁVEIS

## INFO-CLIENTE.md

Aqui tem todas as colunas da tabela de clientes e variáveis extra para personalização

### DADOS DO CLIENTE - PROPOSTA

Dados que serão utilizados nas propostas comerciais:

@dataProposta Por exemplo: "Março 2026"
@numeroProposta; "SESI26102"
@nomeProposta; "Assessoria e Projeto"
@cidadeProposta; "Goiânia"
@localProposta; "Rua C152, Qd 345, Lt. 07, Jardim América, Goiânia, Goiás"
@geolocalizacaoProposta; "-16.7149004-49.2803072"
@nomeCliente; "Simone e Sebastião"
@empregoCliente; "Advogados"
@estadoCivilCliente; "Casados"
@cpfCnpjCliente; "000.000.000-00"
@enderecoCliente; "Rua C152"

## INFO-SERVICO.md

@TEMPLATE; 02-COD_DOC_PC_00_R00_PROPOSTA_VIABILIDADE.pptx

### DADOS BÁSICOS

@DataAtual; "07 de Maio de 2026"

### DADOS DO CLIENTE - CONTRATO

O cliente pode precisar utilizar dados distintos no contrato, portanto abaixo tem os dados para a contratação do serviço:

@nomeContrato; "Assessoria Técnica e Projeto de Interiores"
@numeroContrato; "CTR-2026-79937"
@nomeClienteContrato; "Simone e Sebastião"
@estadoCivilClienteContrato; "Casados"
@empregoClienteContrato; "Advogados"
@telefoneClienteContrato; "62 99999-9999"
@emailClienteContrato; "cliente@email.com"

### DADOS DO SERVIÇO

@modalidadeServico; "Assessoria Técnica e Projeto de Interiores"
@anoProjeto; "2026"
@demandaProposta; "Reforma de Interiores"
@areaTotal; 73.71
@areaCoberta; 68.41
@areaDescoberta; 5.30
@detalhesProposta;Descrição detalhada sobre os objetivos e necessidades da proposta, como o tipo de estudo ou desenvolvimento do projeto
@estiloProjeto;Estilo do projeto arquitetônico, exemplo: "Contemporâneo-funcionalista"
@ambientesProjeto;Lista de ambientes planejados para o projeto, exemplo: Sala, 2 Quartos, Cozinha, Banheiro social, etc.
@inProposta;Data de início da proposta, exemplo: Outubro
@lvProposta;Data de levantamento de viabilidade, exemplo: Outubro
@anProposta;Data de análise da proposta, exemplo: Outubro
@baProposta;Data de conclusão do estudo de viabilidade, exemplo: Novembro
@prProposta;Data de aprovação preliminar da proposta, exemplo: Novembro
@inSolucao;Data de início da solução final, exemplo: Novembro
@valorProposta; Valor total da proposta inicial, exemplo: 2066.77
@valorContrato; Valor a ser realizado no contrato.

#### DADOS PARA ESTIMATIVA DE CUSTO - PROPOSTA

@projArqEng;Custo estimado dos projetos de arquitetura e engenharia, exemplo: 35347.55
@procLegais;Custo estimado dos processos legais, exemplo: 4241.70
@ACEqv;[calculo: @areaCoberta] Valor baseado na área construída equivalente
@execcub;[calculo: 1300*@ACEqv] Custo de execução baseado no CUB multiplicado pela ACEqv
@execInfra;[calculo: @execcub*0.20] Custo de execução de infraestrutura
@execPais;[calculo: @execcub*0.05] Custo de execução de paisagism
@execMob;[calculo: @execcub*0.05] Custo de execução de mobiliário
@totalParcial;[calculo: @projArqEng+@procLegais] Soma dos custos parciais
@totalExec;[calculo: @execcub+@execInfra+@execPais] Soma dos custos de execução
@totalinss;[calculo:  @execcub*0.20] Soma das contribuições ao INSS
@totalGeral;[calculo: @totalParcial+@totalExec+@totalinss] Soma do total parcial, total de execução e total de INSS
@ArqEng%;[calculo: @projArqEng/@totalGeral] Percentual do custo de projetos de arquitetura e engenharia em relação ao total
@Legais%;[calculo: @procLegais/@totalGeral] Percentual do custo de processos legais em relação ao total
@precoCUB%;[calculo: @execcub/@totalGeral] Percentual do custo baseado no CUB em relação ao total
@Parcial%;[calculo: @totalParcial/@totalGeral] Percentual do total parcial em relação ao total geral
@infra%;[calculo: @execInfra/@totalGeral] Percentual do custo de infraestrutura em relação ao total
@pais%;[calculo: @execPais/@totalGeral] Percentual do custo de paisagismo em relação ao total
@mob%;[calculo: @execMob/@totalGeral] Percentual do custo de mobiliário em relação ao total
@Exec%;[calculo: @totalExec/@totalGeral] Percentual do custo de execução em relação ao total
@inss%;[calculo: @totalinss/@totalGeral] Percentual da contribuição ao INSS em relação ao total
