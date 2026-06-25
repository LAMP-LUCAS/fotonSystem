# EPIC-004: Recuperação Inteligente de Conhecimento (RAG)

**Data:** 2026-06-25
**Stakeholders:** Equipe do escritório (todos os usuários), Time Core (manutenção)
**Métrica de Sucesso:** 90% das consultas retornam resultado relevante na primeira busca

## Dor Atual

O Foton System possui um motor de busca semântica (RAG via ChromaDB), mas ele não é usado no cotidiano do escritório:

- **Indexação esquecível:** A indexação do conhecimento é manual e fácil de esquecer. O usuário indexa uma vez e nunca mais, tornando a base desatualizada.
- **Resultados sem contexto:** A busca retorna trechos de texto, mas não informa de qual cliente, serviço ou arquivo aquele trecho veio. O usuário não consegue agir sobre o resultado.
- **Fora da TUI:** A busca semântica só está disponível via MCP (agentes de IA). O usuário comum não tem acesso a ela pela interface de texto.
- **Falha silenciosa do ChromaDB:** Quando o banco vetorial está indisponível (corrompido, versão incompatível), a consulta retorna vazio sem aviso. O usuário acha que não há dados.
- **Sem filtro:** A busca varre todo o acervo sem possibilidade de filtrar por cliente, serviço ou tipo de documento.

## Critérios de Sucesso do Negócio

- [ ] Indexação automática sempre que um INFO-*.md for criado ou alterado (gatilho do File Watcher)
- [ ] Resultados da busca exibem nome do cliente, serviço e arquivo de origem com caminho para navegação direta
- [ ] Busca semântica integrada à TUI via atalho dedicado (ex: `g` de "global search")
- [ ] Fallback gracioso com mensagem clara quando ChromaDB estiver indisponível, incluindo sugestão de re-indexação
- [ ] Filtro de busca opcional por cliente, serviço ou tipo de documento
- [ ] Diagnóstico de integridade do índice com comando para verificar se embeddings correspondem aos arquivos atuais
- [ ] Re-indexação seletiva (apenas um cliente ou serviço, não o acervo inteiro)

## Métricas

- 90% de relevância na primeira busca (avaliação qualitativa trimestral)
- Zero buscas sem resultado por falha de indexação (diagnóstico automático)
- Tempo médio para encontrar informação em projeto passado reduzido de 15 min para 2 min
- Indexação automática em menos de 5 segundos após alteração de arquivo