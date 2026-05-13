---
type: guide
domain: core
status: active
tags: [deploy, release, developer]
---
# Guia de Deploy e Releases (DeploymentGuide)

Este guia descreve como gerar uma nova versão executável do [**FOTON System**](../../README.md) e distribuí-la via GitHub Releases.

## 1. Guia de Instalação (Usuário Final) 👷

### Passo 1: Download

Acesse a aba **[Releases](https://github.com/LAMP-LUCAS/fotonSystem/releases)** do GitHub e baixe o arquivo mais recente:

- `foton_system_vX.X.X.exe`

### Passo 2: Instalação / Atualização

1. Execute o arquivo baixado.
2. O sistema abrirá o menu principal.
3. Para uma instalação limpa (recomendado):
   - Selecione a opção **6 (Configurações / Instalação)**.
   - Siga as etapas para copiar os arquivos para o seu computador.
4. Pronto! Um atalho será criado na sua Área de Trabalho.

> **Nota:** Se você já tem uma versão anterior, o instalador irá atualizar os arquivos automaticamente.

---

## 2. Guia de Deploy (Desenvolvedores) 👩‍💻

Esta seção descreve como **gerar** uma nova versão do sistema.

### Preparação do Ambiente

Certifique-se de que todas as dependências estão instaladas:

```bash
pip install -r requirements.txt
```

**Requisito para Release:**
Para interagir com o GitHub (criar rascunhos de release), você precisa de um **Personal Access Token (PAT)**.

1. Gere um token no GitHub (Settings -> Developer settings -> Personal access tokens).
2. Dê permissão de `repo`.
3. Defina a variável de ambiente `GITHUB_TOKEN` ou tenha o token em mãos.

---

## 2. Deploy Automatizado (Recomendado) 🚀

O script `deploy.py` automatiza todo o processo: Build, Commit na branch `deploy` e Criação do Draft Release.

1. Abra o terminal na raiz do projeto.
2. Execute o script:

    ```bash
    python foton_system/scripts/deploy.py
    ```

3. Siga as instruções interativas:
    - **Build:** O script gera o executável `dist/foton_system_vX.X.X.exe`.
    - **Deploy:** O script envia o executável para a branch `deploy` e cria a tag `vX.X.X`.
    - **Release:** O script cria um Rascunho (Draft) no GitHub com o executável anexado.

---

## 3. Deploy Manual (Fallback) 🛠️

Caso o script automatizado falhe, siga estes passos manuais:

### Passo A: Build

1. Gere o executável com o PyInstaller:

    ```bash
    python foton_system/scripts/build.py
    ```

2. Verifique se o arquivo `dist/foton_system_vX.X.X.exe` foi criado.

### Passo B: Git Deploy

1. Mude para a branch `deploy` (ou crie uma órfã se não existir).
2. Copie o executável gerado e o `foton_system/__init__.py` para a raiz.
3. Commit e Push:

    ```bash
    git add .
    git commit -m "Deploy vX.X.X"
    git tag vX.X.X
    git push origin deploy --tags
    ```

### Passo C: GitHub Release

1. Vá para a página de Releases do GitHub.
2. Clique em "Draft a new release".
3. Escolha a tag `vX.X.X`.
4. Anexe o arquivo `.exe` gerado.
5. Salve como Draft ou Publique.

---

## 4. Publicação e Atualização

### Publicar Release

1. Acesse a página de [Releases do GitHub](https://github.com/LAMP-LUCAS/fotonSystem/releases).
2. Encontre o **Draft** criado.
3. Clique em **Edit**, revise as notas da versão e clique em **Publish release**.

### Atualização do Cliente

O usuário final deve:

1. Acessar a página de Releases.
2. Baixar o `foton_system_vX.X.X.exe` mais recente.
3. Substituir o arquivo antigo em sua máquina.

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Guia do Usuário: [[UserGuide]]
- Plano de Trabalho: [[WorkPlan]]

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.** Veja mais em [Mundo AEC](https://www.mundoaec.com)
