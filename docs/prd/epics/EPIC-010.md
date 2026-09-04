# EPIC-010: Diário de Obra e Atas de Reunião

**Data:** 2026-06-25
**Stakeholders:** Equipe técnica, Gerentes de obra, Administrativo, Clientes finais
**Métrica de Sucesso:** Redução de 70% no tempo de registro e consulta de ocorrências de obra e reuniões

## Dor Atual

Duas atividades diárias essenciais do escritório não têm suporte no Foton System, forçando o uso de cadernos, WhatsApp e planilhas avulsas:

### Diário de Obra
- **Sem registro diário:** Obras não têm um diário formal. Ocorrências (clima, mão de obra, materiais recebidos, intercorrências) são registradas em cadernos ou WhatsApp, sem padronização.
- **Fotografias soltas:** Registros fotográficos da evolução da obra ficam soltos no celular do engenheiro, sem vínculo com o cliente ou data específica.
- **Sem rastro legal:** Em caso de disputa (atraso, vício, acidente), não há registro diário formal que sirva como prova. A responsabilidade é difícil de atribuir.
- **Medição sem base:** A medição de serviços para faturamento não tem lastro no diário de obra — horas trabalhadas, materiais recebidos e serviços executados não são conferíveis.

### Atas de Reunião
- **Reuniões sem ata:** Reuniões com clientes, fornecedores e equipe técnica raramente geram ata formal. Decisões são perdidas ou reinterpretadas.
- **Ações sem dono:** Itens de ação discutidos em reunião não são registrados com responsável e prazo. Compromissos são esquecidos.
- **Sem histórico de decisões:** Não é possível consultar decisões anteriores sobre um mesmo cliente ou serviço. A mesma discussão acontece várias vezes.
- **Aprovações verbais:** Aprovações de projeto, cronograma ou orçamento são verbais. Não há registro formal de "quem aprovou o quê e quando".

## Critérios de Sucesso do Negócio

### Diário de Obra
- [ ] Registro diário por serviço com data, clima, mão de obra (quantidade e função), materiais recebidos, serviços executados e intercorrências
- [ ] Anexo de fotos por registro com legenda e data (caminho para arquivos no filesystem)
- [ ] Template padronizado de diário de obra exportável para PDF (relatório semanal/mensal)
- [ ] Diário visível na ficha do serviço, ordenado por data decrescente
- [ ] Notificação para equipe quando diário não é preenchido por mais de 3 dias úteis consecutivos
- [ ] Assinatura digital simples (confirmação do responsável) ao fechar o diário do dia

### Atas de Reunião
- [ ] Template de ata com campos: participantes, pauta, decisões, itens de ação (responsável + prazo)
- [ ] Geração de ata a partir de formulário na TUI com salvamento automático
- [ ] Itens de ação exibidos em dashboard de pendências por responsável
- [ ] Notificação automática quando item de ação está próximo do vencimento (48h de antecedência)
- [ ] Histórico de atas por cliente com busca por palavra-chave e data
- [ ] Aprovações registradas em ata com carimbo de data e responsável
- [ ] Exportação de ata formatada em DOCX/PDF

## Métricas

- 100% dos dias úteis de obra com diário preenchido
- Zero reuniões com cliente sem ata registrada
- 90% dos itens de ação concluídos no prazo
- Tempo médio para consultar decisão anterior reduzido de 20 min para 2 min

## Dependências

| Este épico depende de | Para fornecer |
|---|---|
| EPIC-002 (Domínio) | Entidades Serviço com vínculo a Cliente |
| EPIC-003 (Documentos) | Engine de templates para exportar ata/diário em DOCX |
| EPIC-007 (Cronograma) | Marcos de obra para referência no diário |
| EPIC-001 (UX TUI) | Formulários e navegação para registro |