# EPIC-002: Domínio, CRUD e Pipeline de Sincronização

**Data:** 2026-06-25
**Stakeholders:** Equipe do escritório (usuários da TUI), Clientes finais (indiretos), Time Core (manutenção)
**Métrica de Sucesso:** Redução de 50% nas interações de suporte relacionadas a "cliente não encontrado" ou inconsistência de dados

## Dor Atual

O FotonSystem evoluiu rapidamente da v1.0 à v1.4, acumulando dívidas estruturais que impactam o uso diário:

- **Dados sem guardrails de integridade:** Códigos de cliente e serviço são strings livres. Não há validação de formato, permitindo inconsistências como "joS01", "JOS1" ou "JOS-01" que quebram buscas e relatórios.
- **Sem possibilidade de remover clientes:** Não há operação de exclusão segura. Clientes cancelados ou duplicados permanecem nas listagens para sempre, poluindo a navegação e gerando confusão.
- **Sincronização confusa:** Sete ferramentas diferentes de sincronização (`sincronizar_clientes`, `sincronizar_pastas_clientes`, `sincronizar_base`, etc.) com nomes similares. O usuário não sabe qual executar e com frequência executa a ferramenta errada, gerando retrabalho.
- **Feedback ausente em operações longas:** Sincronizações e exportações executam sem indicador de progresso, fazendo o usuário achar que o sistema travou.
- **Modelo de entidades incompleto:** As entidades de domínio (Cliente, Serviço) não possuem campos de status com ciclo de vida definido, impedindo operações como filtrar clientes ativos vs. inativos.

## Critérios de Sucesso do Negócio

- [x] Clientes e serviços podem ser removidos com segurança (soft delete) e restaurados se necessário, sem perda de histórico
- [x] Códigos de cliente e serviço seguem formato padronizado, eliminando inconsistências nas buscas
- [ ] Sincronização substituída por pipeline único com pré-visualização (dry-run) antes de aplicar mudanças
- [ ] Modelo de entidades com status migration (Ativo, Inativo, Cancelado) e campos de integridade referencial
- [ ] Operações destrutivas auditadas com POP
- [ ] Ações destrutivas (excluir, sobrescrever) exigem confirmação explícita em padrão único

## Métricas

- Tempo médio para localizar um cliente na lista reduzido em 30%
- Zero consultas de suporte sobre "qual sincronização executar"
- 100% dos clientes e serviços com código em formato válido
- Tempo de sincronização completo reduzido em 40% (operação única vs 7 tools)

## Itens de UX Transferidos

Os itens de UX/navegação que originalmente estavam neste EPIC-002 foram transferidos para o EPIC-001, que agora cobre:

- Breadcrumbs (navegação hierárquica)
- Busca global por cliente
- Indicador de progresso em operações longas
- Padrão de confirmação unificado

## Especificações Técnicas

- SPEC-DOMAIN-CRUD-v1.1 (25 RULE-IDs)
- SPEC-SYNC-v1.0 (10 RULE-IDs)

## Stories Vinculadas

| Story | Status |
|---|---|
| STORY-010: Domain model status migration | ✅ done |
| STORY-011: Domain model entities | ✅ done |
| STORY-012: CRUD delete/restore MCP | ✅ done |
| STORY-013: CRUD financeiro INFO files | ✅ done |
| STORY-014: Pipeline sync unificado | ✅ done |