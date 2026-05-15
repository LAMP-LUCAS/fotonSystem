# ADR 003: Isolamento de Testes via Modo Sandbox

## Status
Proposto

## Contexto
O Foton System manipula dados críticos de escritórios de arquitetura (Excel, arquivos Markdown de clientes e documentos legais). A execução de testes (Unitários, Integração ou E2E) no ambiente de desenvolvimento corre o risco de corromper ou misturar dados de teste com dados reais, especialmente em máquinas onde o sistema está instalado para uso produtivo.

## Decisão
Fica estabelecido que **todos os testes automatizados** devem obrigatoriamente operar em **Modo Sandbox**.

1. **Ativação Obrigatória:** Todo `setUpClass` de suítes de teste de integração ou E2E deve chamar `PathManager.set_sandbox_mode(True)`.
2. **Isolamento de Diretório:** Os testes devem utilizar um subdiretório exclusivo dentro da pasta temporária do sistema (ex: `%TEMP%/foton_tests_XXXX`) para garantir que execuções paralelas não interfiram entre si.
3. **Limpeza Automática:** O `tearDownClass` deve ser responsável por limpar o diretório temporário e desativar o modo sandbox (`set_sandbox_mode(False)`).
4. **Configuração Volátil:** Os testes não devem ler o `settings.json` real do usuário. O `Config()` deve ser reinicializado ou sobreposto com caminhos apontando para o sandbox.

## Consequências
- **Segurança:** Risco zero de deleção ou modificação acidental de dados reais do usuário durante o desenvolvimento.
* **Reprodutibilidade:** Testes rodam em um ambiente "limpo" e controlado, independente da máquina onde estão sendo executados.
* **Complexidade:** Requer um boilerplate consistente em todos os arquivos de teste para garantir que o `PathManager` e o `Config` estejam devidamente isolados.
