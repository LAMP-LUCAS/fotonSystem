---
type: guide
domain: core
status: active
tags: [deploy, release, developer, ci-cd]
---
# Guia de Deploy e Releases (DeploymentGuide)

Este guia descreve como gerar uma nova versão executável do [**FOTON System**](../../README.md) e distribuí-la via GitHub Releases, além do pipeline de CI/CD atual e planejado.

---

## 1. Visão Geral do Pipeline

### Pipeline Atual (v1.2.0)

```
[dev] git commit → pytest manual → build.py → deploy.py (interativo)
                                              ├─ tag vX.X.X
                                              ├─ branch deploy
                                              └─ Draft Release + .zip asset
```

**Características:**
- 100% manual, executado na máquina do desenvolvedor (Windows)
- Sem integração contínua — testes não rodam automaticamente
- Build via PyInstaller com dois modos: `lite` (default, ~90% menor) e `full`
- Deploy interativo via `deploy.py` com prompts em cada etapa
- Branch `deploy` separada funciona como registro de versão para o `UpdateChecker`
- Inno Setup compila instalador Windows profissional

### Pipeline Proposto (GitHub Actions)

```
[push/PR] → CI (pytest + ruff + mypy) → [merge em main]
                                              ↓
                                         [tag v*] → CD (build + release)
                                              ↓
                                     GitHub Release + assets + branch deploy
```

**Características:**
- Automatizado via GitHub Actions
- Qualidade garantida antes do merge (testes + lint + type check)
- Release publicada automaticamente ao criar tag
- Cross-platform: Windows (exe), Linux (server, desktop)

---

## 2. Guia de Instalação (Usuário Final)

### Passo 1: Download

Acesse a aba **[Releases](https://github.com/LAMP-LUCAS/fotonSystem/releases)** do GitHub e baixe o arquivo mais recente:

- `foton_system_vX.X.X.exe` (instalador Inno Setup)
- ou `foton_system_vX.X.X.zip` (portátil, extrair e executar)

### Passo 2: Instalação / Atualização

1. Execute o arquivo baixado.
2. O sistema abrirá o menu principal.
3. Para uma instalação limpa (recomendado):
   - Selecione a opção **6 (Configurações / Instalação)**.
   - Siga as etapas para copiar os arquivos para o seu computador.
4. Pronto! Um atalho será criado na sua Área de Trabalho.

> **Nota:** Se você já tem uma versão anterior, o instalador irá atualizar os arquivos automaticamente. O `UpdateChecker` embutido também notifica o usuário sobre novas versões em runtime.

---

## 3. Arquitetura dos Artefatos

| Artefato | Origem | Finalidade |
|---|---|---|
| `foton_system/__init__.py` | Código fonte | Fonte da verdade da versão (`__version__`) |
| `version.txt` | Gerado pelo `build.py` | Lido pelo Inno Setup para versão do instalador |
| `dist/foton_system_v{version}/` | PyInstaller `--onedir` | Diretório com executável + dependências |
| `dist/foton_system_v{version}.zip` | Gerado pelo `build.py` | Asset para GitHub Release |
| `installer/foton_setup.iss` | Código fonte | Script Inno Setup para instalador Windows |
| Branch `deploy` | `deploy.py` | Registro de versão para `UpdateChecker` |

### Variantes de Build

| Modo | Flag | Tamanho | Inclusões |
|---|---|---|---|
| `lite` (default) | `--type lite` | ~90% menor | Exclui chromadb, torch, transformers, sentence_transformers. Módulos AI instalados on-demand via `DependencyManager` |
| `full` | `--type full` | Completo | Todos os módulos AI inclusos no bundle |

### Targets

| Target | Flag | Plataforma | GUI |
|---|---|---|---|
| Windows Desktop | `--target windows-desktop` | Windows | winshell, pywin32, pythonnet, webview |
| Linux Server | `--target linux-server` | Linux | Headless (sem GUI) |
| Linux Desktop | `--target linux-desktop` | Linux | GUI adapters Linux |

---

## 4. Pipeline Atual — Processo Manual (v1.2.0)

### 4.1 Pré-requisitos

```bash
pip install -r requirements.txt
```

**Para Release no GitHub:** Personal Access Token (PAT) com permissão `repo`.

1. Gere em: GitHub → Settings → Developer settings → Personal access tokens
2. Defina a variável de ambiente `GITHUB_TOKEN` ou informe durante o deploy

### 4.2 Build

```bash
# Build lite (padrão)
python foton_system/scripts/build.py

# Build completo (com AI modules)
python foton_system/scripts/build.py --type full

# Build limpo (sem cache PyInstaller)
python foton_system/scripts/build.py --clean

# Target específico
python foton_system/scripts/build.py --target linux-server
```

**O que o `build.py` faz:**
1. Lê `__version__` de `foton_system/__init__.py`
2. Limpa diretório `dist/` anterior (com retry para locks do OneDrive/antivirus)
3. Escreve `version.txt` para o Inno Setup
4. Executa PyInstaller com hidden imports dinâmicos baseados no modo lite/full
5. Coleta assets, config, scripts, resources, interfaces
6. Gera `dist/foton_system_v{version}.zip`

### 4.3 Deploy Automatizado (Recomendado)

```bash
python foton_system/scripts/deploy.py
```

Script **interativo** que percorre:

| Etapa | Ação | Opcional? |
|---|---|---|
| 1. Build | Executa `build.py` | Sim |
| 2. Tag Git | Cria `git tag v{version}` + `git push --tags` | Sim |
| 3. Branch deploy | Clona/cria branch `deploy`, commita `__init__.py` + README | Sim |
| 4. Draft Release | Gera release notes via `git log`, cria Draft com asset `.zip` | Sim |

### 4.4 Deploy Manual (Fallback)

```bash
# Passo A: Build
python foton_system/scripts/build.py

# Passo B: Git Deploy
git checkout deploy || git checkout --orphan deploy
cp foton_system/__init__.py .
git add .
git commit -m "Deploy vX.X.X"
git tag vX.X.X
git push origin deploy --tags

# Passo C: GitHub Release (via interface web)
# → New Release → tag vX.X.X → anexar .zip → Publish
```

### 4.5 Publicar Release

1. Acesse [Releases do GitHub](https://github.com/LAMP-LUCAS/fotonSystem/releases)
2. Encontre o **Draft** criado pelo `deploy.py`
3. Revise as notas da versão
4. Clique em **Publish release**

---

## 5. Pipeline Proposto — GitHub Actions

> **Status:** Planejado. Implementação prevista após release v1.3.0.

### 5.1 Workflow: CI (`ci.yml`)

**Disparo:** `push` e `pull_request` para `main`

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r requirements-desktop.txt
      - name: Lint
        run: ruff check foton_system/
      - name: Type check
        run: python -m mypy foton_system/
      - name: Test
        run: python -m pytest --tb=short -x
```

**Garantias:**
- 302+ testes passando antes de qualquer merge
- Zero violações de lint (ruff)
- Type hints consistentes (mypy)

### 5.2 Workflow: CD (`release.yml`)

**Disparo:** `tag v*`

```yaml
name: Release
on: [push]
jobs:
  release:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # para release notes via git log
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r requirements-desktop.txt
      - name: Run tests
        run: python -m pytest --tb=short -x
      - name: Build lite
        run: python foton_system/scripts/build.py
      - name: Build full
        run: python foton_system/scripts/build.py --type full
      - name: Generate release notes
        id: notes
        run: |
          $prev = git describe --tags --abbrev=0 HEAD^ 2>$null
          if (-not $prev) { $prev = "v1.0.0" }
          $log = git log "$prev..HEAD" --oneline --no-decorate
          "notes<<EOF" | Out-File $env:GITHUB_OUTPUT -Append
          $log | Out-File $env:GITHUB_OUTPUT -Append
          "EOF" | Out-File $env:GITHUB_OUTPUT -Append
      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          body: ${{ steps.notes.outputs.notes }}
          draft: false
          files: dist/foton_system_v*.zip
      - name: Update deploy branch
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git fetch origin deploy 2>$null || git checkout --orphan deploy
          git checkout deploy
          Copy-Item foton_system/__init__.py .
          git add __init__.py
          git commit -m "Deploy ${{ github.ref_name }}" --allow-empty
          git push origin deploy
```

**Garantias:**
- Build automatizado ao criar tag
- Testes rodam antes do build (qualidade)
- Release publicada (não draft) com assets
- Branch `deploy` atualizada automaticamente

### 5.3 Workflow: Nightly (`nightly.yml`)

**Disparo:** `cron` diário (03:00 UTC)

```yaml
name: Nightly
on:
  schedule:
    - cron: "0 3 * * *"
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r requirements-desktop.txt
      - name: Full test suite
        run: python -m pytest --tb=short
```

**Garantias:**
- Pipeline regredindo detectado em até 24h
- Ideal para equipe ou commits frequentes

---

## 6. Mecanismo de Update em Runtime

Dois componentes buscam atualizações durante a execução do Foton System:

### `UpdateChecker` (branch deploy)

- Arquivo: `foton_system/infrastructure/update_checker.py`
- Busca `__init__.py` em `raw.githubusercontent.com/LAMP-LUCAS/fotonSystem/deploy/`
- Compara `__version__` remoto com local
- Simples e leve (apenas um arquivo)

### `UpdateService` (GitHub Releases API)

- Arquivo: `foton_system/modules/shared/infrastructure/services/update_service.py`
- Usa `api.github.com/repos/LAMP-LUCAS/fotonSystem/releases/latest`
- Mais completo: obtém metadata da release, URLs de download
- Útil para notificar usuários sobre novas versões

---

## 7. Inno Setup — Instalador Windows

**Arquivo:** `installer/foton_setup.iss`

- Lê versão de `version.txt` (gerado pelo `build.py`)
- Instala em `%LOCALAPPDATA%\Programs\FotonSystem`
- Cria atalhos: Start Menu + Área de Trabalho (opcional)
- Desinstalação via Painel de Controle
- Idiomas: Inglês e Português Brasileiro
- Sem necessidade de privilégios administrativos

---

## 8. Roadmap de Melhorias

| Prioridade | Melhoria | Esforço | Impacto |
|---|---|---|---|
| 🔴 P0 | CI com pytest + ruff + mypy em PRs | 2h | Bloqueia merge de código quebrado |
| 🔴 P0 | CD com build + release automático em tag | 3h | Elimina deploy manual |
| 🟡 P1 | Workflow nightly para detecção precoce de regressão | 30min | Pipeline regredindo detectado em 24h |
| 🟡 P1 | Gerar spec file PyInstaller automaticamente | 1h | Elimina `foton_system_v1.1.0.spec` manuais |
| 🟢 P2 | `deploy.py` com modo headless (`--auto`) para Actions | 2h | Script reutilizável em CI e local |
| 🟢 P2 | Build cross-platform (Linux server + desktop) | 4h | Testes reais em Linux |
| 🔵 P3 | Notificação em canal (Discord/Telegram) em falha de CI | 1h | Time sabe imediatamente |
| 🔵 P3 | Análise de cobertura (`pytest-cov`) com badge | 1h | Visibilidade da qualidade |
| ⚪ P4 | Upload automático para PyPI (como biblioteca) | 2h | Distribuição via pip |

---

## 9. Fluxo Completo: PR → Release

```
1. Desenvolvimento na branch feature/
2. PR para main
   ├─ GitHub Actions CI roda: pytest + ruff + mypy
   └─ Merge após aprovação
3. Criar tag vX.X.X em main
   └─ GitHub Actions CD:
        ├─ pytest (garantia dupla)
        ├─ build.py --type lite
        ├─ build.py --type full
        ├─ Criar GitHub Release com assets
        └─ Atualizar branch deploy
4. Inno Setup (opcional, local):
   └─ Compilar instalador e anexar à release
```

---

## 🔗 Links Relacionados
- Índice: [[Index]]
- Guia do Usuário: [[UserGuide]]
- Plano de Trabalho: [[WorkPlan]]
- Log do Projeto: `docs/01_PROJECTS/Sprint_Resiliencia/Log.md`
- Plano da Sprint: `docs/01_PROJECTS/Sprint_Resiliencia/SprintPlan.md`

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.** Veja mais em [Mundo AEC](https://www.mundoaec.com)
