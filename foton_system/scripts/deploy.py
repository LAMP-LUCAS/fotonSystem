import os
import sys
import shutil
import subprocess
import requests
import json
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DIST_DIR = BASE_DIR / "dist"
BUILD_SCRIPT = BASE_DIR / "foton_system" / "scripts" / "build.py"
REPO_OWNER = "LAMP-LUCAS"
REPO_NAME = "fotonSystem"

def run_command(command, cwd=None):
    """Runs a shell command and checks for errors."""
    try:
        subprocess.run(command, check=True, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Erro ao executar comando: {command}")
        print(Fore.RED + str(e))
        sys.exit(1)

def get_version():
    """Extracts version from __init__.py"""
    init_file = BASE_DIR / "foton_system" / "__init__.py"
    with open(init_file, "r") as f:
        for line in f:
            if "__version__" in line:
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.0.0"

def build_executable():
    print(Fore.CYAN + "=== 1. Gerando Executável ===")
    run_command(f"python {BUILD_SCRIPT}", cwd=BASE_DIR)

def git_deploy(version):
    print(Fore.CYAN + f"\n=== 2. Publicando na branch 'deploy' (v{version}) ===")
    
    # Check if git is clean
    if subprocess.run("git status --porcelain", shell=True, capture_output=True).stdout:
        print(Fore.YELLOW + "⚠️  Seu diretório de trabalho não está limpo. Commit suas mudanças antes de fazer deploy.")
        # sys.exit(1) # Warning only, as dist/ changes might be ignored

    temp_deploy_dir = BASE_DIR / "temp_deploy"
    if temp_deploy_dir.exists(): shutil.rmtree(temp_deploy_dir)
    temp_deploy_dir.mkdir()

    # Copy artifacts to temp
    # Copy artifacts to temp
    exe_name = f"foton_system_v{version}.exe"
    exe_path = DIST_DIR / exe_name
    if not exe_path.exists():
        print(Fore.RED + f"Executável não encontrado: {exe_path}")
        sys.exit(1)
    
    shutil.copy2(exe_path, temp_deploy_dir)
    shutil.copy2(BASE_DIR / "foton_system" / "__init__.py", temp_deploy_dir)

    # Switch to deploy branch
    print(Fore.YELLOW + "Alternando para branch 'deploy'...")
    try:
        run_command("git checkout deploy", cwd=BASE_DIR)
    except:
        print(Fore.YELLOW + "Branch 'deploy' não existe. Criando orphan...")
        run_command("git checkout --orphan deploy", cwd=BASE_DIR)
        run_command("git rm -rf .", cwd=BASE_DIR)

    # Copy files back from temp
    print(Fore.YELLOW + "Atualizando arquivos...")
    # Clean current dir (except .git) - simplified by just overwriting/adding
    # In an orphan branch, it's empty. In existing, we might want to clean.
    # For safety, we just copy over.
    
    # Ensure directory structure for __init__.py
    (BASE_DIR / "foton_system").mkdir(exist_ok=True)
    
    shutil.copy2(temp_deploy_dir / exe_name, BASE_DIR / exe_name) # Root in deploy branch? Or dist? User asked for "dist content".
    # User said: "commit do conteúdo de dist para branch deploy". So exe goes to root of deploy branch usually.
    # But let's keep it simple.
    
    shutil.copy2(temp_deploy_dir / "__init__.py", BASE_DIR / "foton_system" / "__init__.py")

    # Git Add & Commit
    run_command("git add .", cwd=BASE_DIR)
    try:
        run_command(f'git commit -m "Deploy v{version}"', cwd=BASE_DIR)
    except:
        print(Fore.YELLOW + "Nada a commitar.")

    # Tag
    tag_name = f"v{version}"
    try:
        run_command(f"git tag {tag_name}", cwd=BASE_DIR)
    except:
        print(Fore.YELLOW + f"Tag {tag_name} já existe. Atualizando...")
        run_command(f"git tag -d {tag_name}", cwd=BASE_DIR)
        run_command(f"git tag {tag_name}", cwd=BASE_DIR)

    # Push
    print(Fore.YELLOW + "Enviando para GitHub...")
    run_command("git push origin deploy", cwd=BASE_DIR)
    run_command("git push origin --tags", cwd=BASE_DIR)

    # Cleanup and Switch back
    print(Fore.YELLOW + "Voltando para main...")
    run_command("git checkout main", cwd=BASE_DIR)
    shutil.rmtree(temp_deploy_dir)

def create_github_release(version, token):
    print(Fore.CYAN + f"\n=== 3. Criando Rascunho de Release (v{version}) ===")
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "tag_name": f"v{version}",
        "target_commitish": "deploy",
        "name": f"Versão {version}",
        "body": f"Release automatizado da versão {version}.\n\n**Novidades:**\n- ...",
        "draft": True,
        "prerelease": False
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        release = response.json()
        print(Fore.GREEN + f"Release criado: {release['html_url']}")
        upload_url = release['upload_url'].replace("{?name,label}", "")
        
        # Upload Asset
        asset_path = DIST_DIR / f"foton_system_v{version}.exe"
        print(Fore.YELLOW + f"Fazendo upload do executável ({asset_path.name})...")
        
        with open(asset_path, 'rb') as f:
            headers['Content-Type'] = 'application/octet-stream'
            upload_resp = requests.post(
                f"{upload_url}?name={asset_path.name}",
                headers=headers,
                data=f
            )
            if upload_resp.status_code == 201:
                print(Fore.GREEN + "Upload concluído com sucesso!")
            else:
                print(Fore.RED + f"Erro no upload: {upload_resp.text}")
    else:
        print(Fore.RED + f"Erro ao criar release: {response.text}")

def main():
    print(Fore.GREEN + "=== AUTOMAÇÃO DE DEPLOY FOTON SYSTEM ===\n")
    
    version = get_version()
    print(f"Versão detectada: {Style.BRIGHT}{version}{Style.RESET_ALL}")
    
    # 1. Build
    if input("Executar Build? (S/N): ").lower() == 's':
        build_executable()
    
    # 2. Git Deploy
    if input("Realizar Deploy para branch 'deploy'? (S/N): ").lower() == 's':
        git_deploy(version)
    
    # 3. GitHub Release
    if input("Criar Draft Release no GitHub? (S/N): ").lower() == 's':
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            print(Fore.YELLOW + "Token do GitHub não encontrado nas variáveis de ambiente.")
            token = input("Insira seu GitHub Personal Access Token (repo scope): ").strip()
        
        if token:
            create_github_release(version, token)
        else:
            print(Fore.RED + "Token não fornecido. Pulando criação de release.")

if __name__ == "__main__":
    main()
