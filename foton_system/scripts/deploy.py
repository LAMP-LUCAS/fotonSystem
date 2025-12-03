import os
import sys
import shutil
import subprocess
import requests
import time
from pathlib import Path
from colorama import init, Fore, Style

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Initialize colorama
init(autoreset=True)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DIST_DIR = BASE_DIR / "dist"
BUILD_SCRIPT = BASE_DIR / "foton_system" / "scripts" / "build.py"
REPO_OWNER = "LAMP-LUCAS"
REPO_NAME = "fotonSystem"

def run_command(command, cwd=None, check=True):
    """Runs a shell command and checks for errors."""
    try:
        result = subprocess.run(command, check=check, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0 and check:
            print(Fore.RED + f"Erro ao executar comando: {command}")
            print(Fore.RED + result.stderr)
            sys.exit(1)
        return result
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Erro crítico ao executar: {command}")
        print(Fore.RED + str(e))
        sys.exit(1)

def get_version():
    """Extracts version from __init__.py"""
    init_file = BASE_DIR / "foton_system" / "__init__.py"
    if not init_file.exists():
        print(Fore.RED + "Arquivo __init__.py não encontrado!")
        sys.exit(1)
        
    with open(init_file, "r", encoding="utf-8") as f:
        for line in f:
            if "__version__" in line:
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.0.0"

def build_executable():
    print(Fore.CYAN + "=== 1. Gerando Executável ===")
    run_command(f"python {BUILD_SCRIPT}", cwd=BASE_DIR)

def check_remote_tag(version):
    """Checks if tag already exists on remote."""
    print(Fore.YELLOW + f"Verificando tag v{version} no remoto...")
    cmd = f"git ls-remote --tags origin v{version}"
    result = run_command(cmd, cwd=BASE_DIR, check=False)
    return bool(result.stdout.strip())

def safe_remove(path, retries=3):
    """Safely removes a directory or file with retries."""
    path = Path(path)
    if not path.exists():
        return

    for i in range(retries):
        try:
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=False)
            else:
                path.unlink()
            return
        except PermissionError:
            if i < retries - 1:
                print(Fore.YELLOW + f"Arquivo em uso. Tentando novamente em 2s... ({i+1}/{retries})")
                time.sleep(2)
            else:
                # If delete fails, try to rename to move it out of the way
                try:
                    timestamp = int(time.time())
                    trash_path = path.parent / f"{path.name}_trash_{timestamp}"
                    path.rename(trash_path)
                    print(Fore.YELLOW + f"Aviso: {path} renomeado para {trash_path} (arquivo em uso).")
                    return
                except Exception as rename_err:
                    print(Fore.RED + f"Erro crítico: Não foi possível remover nem renomear {path}: {rename_err}")
                    sys.exit(1)
        except Exception as e:
            print(Fore.RED + f"Erro ao remover {path}: {e}")
            sys.exit(1)

def tag_main_branch(version):
    """Tags the current branch (main) and pushes to remote."""
    print(Fore.CYAN + f"\n=== 2. Criando Tag v{version} na branch atual ===")
    
    # Check if git is clean
    if run_command("git status --porcelain", cwd=BASE_DIR, check=False).stdout.strip():
        print(Fore.YELLOW + "⚠️  Seu diretório de trabalho não está limpo.")
        if input("Deseja continuar e taggear o estado atual? (S/N): ").lower() != 's':
            return False

    tag_name = f"v{version}"
    
    # Check remote tag
    if check_remote_tag(version):
        print(Fore.RED + f"A tag {tag_name} já existe no repositório remoto.")
        choice = input("Deseja sobrescrever a tag existente? (S/N): ").lower()
        if choice != 's':
            print(Fore.YELLOW + "Operação cancelada pelo usuário.")
            return False
        # Delete remote tag to allow overwrite
        print(Fore.YELLOW + "Removendo tag remota antiga...")
        run_command(f"git push --delete origin {tag_name}", cwd=BASE_DIR, check=False)

    # Tag Management Locally
    print(Fore.YELLOW + f"Criando tag local {tag_name}...")
    # Remove local tag if exists to avoid conflict
    run_command(f"git tag -d {tag_name}", cwd=BASE_DIR, check=False)
    run_command(f"git tag {tag_name}", cwd=BASE_DIR)

    print(Fore.YELLOW + "Enviando tag para o GitHub...")
    run_command(f"git push origin {tag_name}", cwd=BASE_DIR)
    return True

def git_deploy_metadata(version):
    print(Fore.CYAN + f"\n=== 3. Atualizando branch 'deploy' (Histórico) ===")
    
    deploy_dir = BASE_DIR / "deploy_release"
    safe_remove(deploy_dir)
    deploy_dir.mkdir(exist_ok=True)

    # 1. Clone the repo (single branch) to temp dir
    print(Fore.YELLOW + "Clonando branch 'deploy'...")
    repo_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}.git"
    
    # Ensure dir is empty before cloning if it wasn't removed
    if any(deploy_dir.iterdir()):
        print(Fore.YELLOW + "Diretório não vazio. Tentando limpar...")
        for item in deploy_dir.iterdir():
            safe_remove(item)

    clone_cmd = f"git clone --branch deploy --single-branch {repo_url} ."
    result = run_command(clone_cmd, cwd=deploy_dir, check=False)
    
    if result.returncode != 0:
        print(Fore.YELLOW + "Branch 'deploy' não encontrada. Criando nova (orphan)...")
        run_command(f"git clone {repo_url} .", cwd=deploy_dir)
        run_command("git checkout --orphan deploy", cwd=deploy_dir)
        run_command("git rm -rf .", cwd=deploy_dir)

    # 2. Clean directory (keep .git)
    for item in deploy_dir.iterdir():
        if item.name != ".git":
            safe_remove(item)

    # 3. Create Metadata
    print(Fore.YELLOW + "Criando metadados da versão...")
    with open(deploy_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(f"# FOTON System v{version}\n\n")
        f.write(f"O executável desta versão está disponível na aba [Releases](../../releases/tag/v{version}).\n")
        f.write("\nEste branch contém apenas metadados da versão para rastreabilidade.")
    
    (deploy_dir / "foton_system").mkdir(exist_ok=True)
    shutil.copy2(BASE_DIR / "foton_system" / "__init__.py", deploy_dir / "foton_system" / "__init__.py")

    # 4. Commit and Push
    print(Fore.YELLOW + "Enviando log para GitHub...")
    run_command("git add .", cwd=deploy_dir)
    
    commit_msg = f"Deploy Log v{version}"
    if run_command("git status --porcelain", cwd=deploy_dir, check=False).stdout.strip():
        run_command(f'git commit -m "{commit_msg}"', cwd=deploy_dir)
        run_command("git push origin deploy", cwd=deploy_dir)
    else:
        print(Fore.YELLOW + "Nenhuma mudança no log.")

    # Cleanup
    print(Fore.YELLOW + "Limpando arquivos temporários...")
    safe_remove(deploy_dir)

def generate_release_body(version):
    """Generates a rich release body with changelog."""
    print(Fore.YELLOW + "Gerando notas de lançamento...")
    
    # Get Changelog
    try:
        # Try to find the previous tag
        prev_tag = run_command("git describe --tags --abbrev=0 HEAD^", cwd=BASE_DIR, check=False).stdout.strip()
        if prev_tag:
            log_range = f"{prev_tag}..HEAD"
        else:
            log_range = "HEAD"
            
        changelog = run_command(f'git log {log_range} --pretty=format:"- %s"', cwd=BASE_DIR, check=False).stdout.strip()
    except Exception:
        changelog = "- Detalhes não disponíveis automaticamente."

    if not changelog:
        changelog = "- Melhorias gerais e correções de bugs."

    template = f"""# 🚀 FOTON System v{version} - Potência para seus Projetos!

Estamos entusiasmados em apresentar a versão **{version}** do FOTON System! 🏗️✨
Nossa missão é transformar a gestão de arquitetura e engenharia, e esta atualização é mais um passo nessa jornada.

## 🌟 O que há de novo?

> *[Espaço reservado para destaques manuais]*

## 🛠️ Changelog Técnico

{changelog}

---
**Instalação:**
1. Baixe o arquivo `foton_system_v{version}.exe` abaixo.
2. Execute em sua máquina (Windows).

*Feito com ❤️ para a comunidade AEC.*"""
    return template

def create_github_release(version, token):
    print(Fore.CYAN + f"\n=== 4. Criando Rascunho de Release (v{version}) ===")
    
    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    })
    
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    
    release_body = generate_release_body(version)

    # Check if release already exists
    resp = session.get(f"{api_url}/releases/tags/v{version}")
    if resp.status_code == 200:
        print(Fore.YELLOW + f"Release v{version} já existe. Editando...")
        release_url = resp.json()['url']
        # Update body for existing release
        session.patch(release_url, json={"body": release_body})
    else:
        # Create new draft release
        data = {
            "tag_name": f"v{version}",
            # "target_commitish": "main", # Optional: defaults to the tag's commit
            "name": f"Versão {version}",
            "body": release_body,
            "draft": True,
            "prerelease": False
        }
        resp = session.post(f"{api_url}/releases", json=data)
        if resp.status_code != 201:
            print(Fore.RED + f"Erro ao criar release: {resp.text}")
            return
        release_url = resp.json()['url']
        print(Fore.GREEN + f"Rascunho criado: {resp.json()['html_url']}")

    # Upload Asset
    exe_name = f"foton_system_v{version}.exe"
    asset_path = DIST_DIR / exe_name
    
    if not asset_path.exists():
        print(Fore.RED + f"Arquivo não encontrado para upload: {asset_path}")
        return

    # Check file size
    file_size_mb = asset_path.stat().st_size / (1024 * 1024)
    print(Fore.YELLOW + f"Preparando upload de {exe_name} ({file_size_mb:.2f} MB)...")
    
    if file_size_mb > 2000: # GitHub limit is 2GB
        print(Fore.RED + "Arquivo excede o limite de 2GB do GitHub Releases.")
        return

    # Get upload URL
    release_data = session.get(release_url).json()
    upload_url = release_data['upload_url'].replace("{?name,label}", "")
    
    # Check if asset already exists and delete it
    for asset in release_data.get('assets', []):
        if asset['name'] == exe_name:
            print(Fore.YELLOW + "Asset já existe. Substituindo...")
            session.delete(asset['url'])
            break

    # Perform Upload
    with open(asset_path, 'rb') as f:
        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": str(asset_path.stat().st_size)
        }
        upload_resp = session.post(
            f"{upload_url}?name={exe_name}",
            headers=headers,
            data=f,
            timeout=300 # 5 minutes timeout for large files
        )
        
        if upload_resp.status_code == 201:
            print(Fore.GREEN + "✅ Upload concluído com sucesso!")
        else:
            print(Fore.RED + f"❌ Falha no upload: {upload_resp.status_code} - {upload_resp.text}")

def main():
    print(Fore.GREEN + "=== AUTOMAÇÃO DE DEPLOY FOTON SYSTEM ===\n")
    
    try:
        version = get_version()
        print(f"Versão detectada: {Style.BRIGHT}{version}{Style.RESET_ALL}")
        
        # 1. Build
        if input("Executar Build? (S/N): ").lower() == 's':
            build_executable()
        
        # 2. Tag Main Branch
        tag_success = False
        if input("Criar Tag na branch atual (Main)? (S/N): ").lower() == 's':
            tag_success = tag_main_branch(version)
        
        # 3. Deploy Metadata (Log)
        if input("Atualizar branch 'deploy' (Log)? (S/N): ").lower() == 's':
            git_deploy_metadata(version)

        # 4. GitHub Release
        if input("Criar/Atualizar Release no GitHub? (S/N): ").lower() == 's':
            if not tag_success:
                print(Fore.YELLOW + "Atenção: A tag não foi criada/atualizada nesta execução.")
                if input("Continuar com a release mesmo assim? (S/N): ").lower() != 's':
                    return

            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                print(Fore.YELLOW + "Token do GitHub não encontrado nas variáveis de ambiente.")
                token_input = input("Insira seu GitHub Personal Access Token (repo scope): ").strip()
                if token_input:
                    token = token_input
            
            if token:
                create_github_release(version, token)
            else:
                print(Fore.RED + "Token não fornecido. Operação cancelada.")

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nOperação interrompida pelo usuário.")
    except Exception as e:
        print(Fore.RED + f"\nErro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
