# 🚀 FOTON System v1.2.0: Modularidade, Alta Performance e Didática

### 🧠 A Versão da Maturidade Agêntica

A **v1.2.0** é o lançamento mais ambicioso do FOTON System até agora. Transformamos uma ferramenta CLI robusta em um ecossistema inteligente, leve e que ensina o usuário enquanto ele trabalha. Focamos em três pilares: **Rapidez Total**, **Flexibilidade de Dados** e **Aprendizado Orgânico**.

---

### 1. ⚡ Novo Terminal Rápido (TUI Form Filler)
Substituímos o fluxo sequencial por uma **Interface Interativa de Terminal** inspirada em editores profissionais.
- **Navegação Não-Linear:** Vá e volte entre campos com `[N]` e `[P]`. Aperte `ENTER` para manter dados originais.
- **Visualizador de Alta Fidelidade (Preview):** Aperte `[V]` para ver o arquivo Markdown completo renderizado na tela, com cores que destacam o que você editou (Ciano), o que é calculado (Verde) e o texto original (Cinza).
- **Cálculos Matemáticos Instantâneos:** Áreas, custos e taxas são recalculados no terminal no milissegundo em que você altera um dado.
- **Versionamento Nativo:** Nova função **[A] Salvar Como** permite criar versões (v1, v2, final) dos seus arquivos de dados sem esforço.

### 2. 🧬 Unificação de DNA (Templates INFO)
Agora você é o mestre da estrutura dos seus projetos.
- **DNA Centralizado:** O sistema agora usa um único arquivo mestre (`info-Template.md`) como base para todos os novos clientes e serviços.
- **Customização Total:** Adicionada a configuração `caminho_template_info` no `settings.json`. Você pode criar o seu próprio padrão de escritório e o Foton o seguirá.
- **Hierarquia SSOT (Single Source of Truth):** Implementamos a resolução em camadas. O sistema busca dados no Documento > Serviço > Cliente, garantindo que você nunca digite o mesmo dado duas vezes.

### 3. 📦 Arquitetura Modular (Plugins On-Demand)
O Foton System agora é leve ("Lite" por padrão).
- **Adeus Build Pesado:** O executável principal foi reduzido em 90%. Bibliotecas de IA (`torch`, `chromadb`) só são instaladas se você decidir usar a Memória Semântica.
- **DependencyManager:** Um novo gestor que cria ambientes virtuais (`venv`) isolados em seu computador para plugins pesados, mantendo o sistema limpo e rápido.
- **Builds Dual:** Suporte a `--type lite` (rápido/pequeno) e `--type full` (completo/offline).

### 4. 🎓 Sistema de Didática Integrada (Docs-as-UI)
A documentação agora ganha vida dentro do programa.
- **TipService:** O sistema varre seus manuais em busca de tags `[!DIDACTIC]` e as exibe como dicas no rodapé.
- **Aprendizado Contextual:** Receba dicas sobre formatação de aspas em anos e códigos exatamente no momento em que está preenchendo a ficha.

### 5. 🛡️ Resiliência e Estabilidade no Windows
- **Integração WebView2:** Interface visual moderna com suporte nativo a Edge/Chromium.
- **Fallback Automático:** Se a interface nativa falhar ou estiver lenta, o sistema abre automaticamente no seu navegador padrão.
- **Instalador de Elite:** O `InstallService` agora sobrevive a arquivos bloqueados pelo OneDrive e Antivírus, garantindo uma atualização suave (Opção 7).
- **Correção de Dependências:** Estabilidade total para `PIL` (imagens), `pandas.plotting` e `jaraco`.

---

### 🛠️ Como Atualizar

1. Baixe o novo `foton_system_v1.2.0.zip`.
2. Extraia e execute o `foton_system_v1.2.0.exe`.
3. Para agilidade extrema no preenchimento de propostas, use a **Opção [3] -> [2] (Terminal Rápido)**.

*Potencializando arquitetos com código leve, concreto inteligente e ensino contínuo.* 🏗️✨

---

**Full Changelog**: <https://github.com/LAMP-LUCAS/fotonSystem/commits/v1.2.0>
