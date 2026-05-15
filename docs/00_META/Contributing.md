---
type: guide
domain: core
status: active
tags: [contributing, development, collaboration]
---
# Contribuindo para o FOTON System (Contributing)

Obrigado pelo interesse em contribuir para o FOTON System! 🎉
Este documento define as diretrizes para garantir que a colaboração seja produtiva e organizada.

## Código de Conduta

Esperamos que todos os colaboradores sejam respeitosos, inclusivos e profissionais. Comentários ofensivos ou discriminatórios não serão tolerados.

## Como Contribuir

### 1. Preparar o Ambiente

1. **Fork** este repositório.
2. **Clone** o seu fork:

    ```bash
    git clone https://github.com/SEU-USUARIO/fotonSystem.git
    cd fotonSystem
    ```

3. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

### 2. Criar uma Branch

Nunca trabalhe direto na `main`. Crie uma branch descritiva para sua tarefa:

* **Funcionalidades:** `feat/nome-da-feature`
* **Correções:** `fix/nome-do-bug`
* **Documentação:** `docs/o-que-mudou`

```bash
git checkout -b feat/nova-funcionalidade
```

### 3. Padrão de Commits

Nossos commits devem ser **Atômicos** e em **Português do Brasil**.

* **Bom:** `feat: adiciona validação de CPF no cadastro de clientes`
* **Ruim:** `ajustes`, `fix`, `update`

Use os prefixos convencionais:

* `feat:` Nova funcionalidade.
* `fix:` Correção de bug.
* `docs:` Alteração apenas na documentação.
* `style:` Formatação, ponto e vírgula, etc (sem mudar lógica).
* `refactor:` Refatoração de código.

### 4. Enviar Pull Request (PR)

1. Faça o push da sua branch: `git push origin feat/nova-funcionalidade`.
2. Abra um Pull Request no repositório original.
3. Descreva claramente o que foi feito e, se possível, anexe prints ou evidências de teste.

### 5. Versionamento e Tags

Adotamos o **Versionamento Semântico (SemVer)**: `vMAJOR.MINOR.PATCH` (ex: `v1.2.3`).

* **MAJOR**: Mudanças incompatíveis na API ou quebra de compatibilidade.
* **MINOR**: Novas funcionalidades compatíveis com versões anteriores.
* **PATCH**: Correções de bugs compatíveis com versões anteriores.

**Como criar uma Tag:**
Ao finalizar uma versão estável na branch `main`:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Isso disparará o processo de Release se estiver configurado.

## Reportando Bugs

Ao abrir uma Issue, por favor inclua:

* Passos para reproduzir o erro.
* Comportamento esperado vs. comportamento real.
* Screenshots ou logs de erro.

Obrigado por ajudar a construir o FOTON System! 🚀

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Manifesto: [[SystemManifest]]
- Protocolo: [[LlmProtocol]]
