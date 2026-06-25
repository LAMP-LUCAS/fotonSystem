# EPIC-002: Domínio, CRUD e Evolução da Experiência do Usuário

**Data:** 2026-06-25
**Stakeholders:** Equipe do escritório (usuários da TUI), Clientes finais (indiretos), Time Core (manutenção)
**Métrica de Sucesso:** Redução de 50% nas interações de suporte relacionadas a "cliente não encontrado" ou inconsistência de dados

## Dor Atual

O FotonSystem evoluiu rapidamente da v1.0 à v1.4, acumulando dívidas estruturais que impactam o uso diário:

- **Dados sem guardrails de integridade:** Códigos de cliente e serviço são strings livres. Não há validação de formato, permitindo inconsistências como "joS01", "JOS1" ou "JOS-01" que quebram buscas e relatórios.
- **Sem possibilidade de remover clientes:** Não há operação de exclusão segura. Clientes cancelados ou duplicados permanecem nas listagens para sempre, poluindo a navegação e gerando confusão.
- **Sincronização confusa:** Sete ferramentas diferentes de sincronização (`sincronizar_clientes`, `sincronizar_pastas_clientes`, `sincronizar_base`, etc.) com nomes similares. O usuário não sabe qual executar e com frequência executa a ferramenta errada, gerando retrabalho.
- **Navegação TUI sem orientação:** Menus longos sem breadcrumbs. O usuário se perde na hierarquia e não sabe em qual tela está. Não há busca global para encontrar clientes rapidamente.
- **Feedback ausente em operações longas:** Sincronizações e exportações executam sem indicador de progresso, fazendo o usuário achar que o sistema travou.

## Critérios de Sucesso do Negócio

- [ ] Clientes e serviços podem ser removidos com segurança (soft delete) e restaurados se necessário, sem perda de histórico
- [ ] Códigos de cliente e serviço seguem formato padronizado, eliminando inconsistências nas buscas
- [ ] Sincronização substituída por pipeline único com pré-visualização (dry-run) antes de aplicar mudanças
- [ ] Toda tela exibe breadcrumbs mostrando onde o usuário está na hierarquia
- [ ] Busca global disponível para localizar qualquer cliente por nome, código ou documento
- [ ] Operações demoradas exibem barra de progresso
- [ ] Ações destrutivas (excluir, sobrescrever) exigem confirmação explícita em padrão único
- [ ] Operações destrutivas são auditadas com POP

## Métricas

- Tempo médio para localizar um cliente na lista reduzido em 30%
- Zero consultas de suporte sobre "qual sincronização executar"
- 100% dos clientes e serviços com código em formato válido
- Tempo de sincronização completo reduzido em 40% (operação única vs 7 tools)
