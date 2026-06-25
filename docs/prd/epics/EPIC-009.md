# EPIC-009: Conformidade, Rastreabilidade e Perenidade

**Data:** 2026-06-25
**Stakeholders:** Sócios, Administrativo, Fiscal, Time Core (manutenção)
**Métrica de Sucesso:** Zero multas ou paralisações por documentação vencida e recuperação de dados em menos de 15 minutos

## Dor Atual

O escritório opera sem garantias mínimas de conformidade legal e segurança de dados, expondo o negócio a riscos evitáveis:

- **Documentos legais sem controle:** Licenças, alvarás, certidões e contratos têm data de validade, mas não há alerta de vencimento. Multas e paralisações ocorrem por esquecimento.
- **Sem backup confiável:** A base de dados do Foton (Excel) fica apenas no computador do escritório. Um formato de HD, roubo ou corrupção de arquivo significa perda de todos os dados.
- **Rastreabilidade apenas técnica:** Os logs de auditoria (POP) existem em JSONL, mas são inacessíveis ao usuário comum. Não há um painel de "quem fez o quê e quando".
- **Sem versionamento:** Alterações em INFO-*.md sobrescrevem o conteúdo anterior. Não é possível recuperar uma versão antiga de um dado do cliente.
- **Dossiê manual:** Para due diligence, venda do escritório ou captação de crédito, é necessário montar um dossiê de cada cliente manualmente, reunindo contratos, certidões e financeiro.

## Critérios de Sucesso do Negócio

- [ ] Cadastro de documentos legais por cliente e serviço com tipo, número, data de emissão e validade
- [ ] Alerta de vencimento configurável (30, 15, 7, 1 dia de antecedência)
- [ ] Backup automatizado da base de dados em nuvem (Google Drive, OneDrive ou S3) com retenção de 30 dias
- [ ] Versionamento de INFO-*.md com capacidade de restaurar versão anterior
- [ ] Painel de auditoria acessível na TUI com filtro por cliente, operação e período
- [ ] Geração de dossiê completo do cliente (contratos, certidões, financeiro, cronograma) em PDF
- [ ] Exportação de relatório de conformidade geral do escritório para auditoria externa

## Métricas

- Zero vencimentos não notificados com pelo menos 7 dias de antecedência
- Backup recuperável em menos de 15 minutos
- 100% das operações destrutivas registradas no painel de auditoria
- Tempo para gerar dossiê de cliente reduzido de 4 horas para 10 minutos