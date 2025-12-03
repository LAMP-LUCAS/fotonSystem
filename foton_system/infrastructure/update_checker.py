import requests
import re
import webbrowser
from colorama import Fore, Style
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system import __version__

class UpdateChecker:
    def __init__(self):
        self.config = Config()
        # Hardcoded for security
        self.repo_url = "https://github.com/LAMP-LUCAS/fotonSystem"
        self.current_version = __version__

    def check_for_updates(self):
        """
        Checks for updates by fetching the __init__.py from the deploy branch.
        Returns: (has_update, latest_version, release_url)
        """
        try:
            # Construct raw URL for __init__.py in deploy branch
            # Assumes repo_url is like https://github.com/user/repo
            if "github.com" not in self.repo_url:
                return False, None, None

            # Convert github.com/user/repo -> raw.githubusercontent.com/user/repo/deploy/foton_system/__init__.py
            raw_url = self.repo_url.replace("github.com", "raw.githubusercontent.com")
            raw_url = f"{raw_url}/deploy/foton_system/__init__.py"
            
            response = requests.get(raw_url, timeout=3)
            if response.status_code == 200:
                remote_version = self._parse_version(response.text)
                if remote_version and self._is_newer(remote_version, self.current_version):
                    return True, remote_version, f"{self.repo_url}/releases"
            
            return False, None, None
        except Exception:
            return False, None, None

    def _parse_version(self, content):
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        return None

    def _is_newer(self, remote, current):
        try:
            r_parts = [int(x) for x in remote.split('.')]
            c_parts = [int(x) for x in current.split('.')]
            return r_parts > c_parts
        except ValueError:
            return False

    def prompt_update(self):
        print(f"\n{Fore.CYAN}Verificando atualizações...{Style.RESET_ALL}")
        has_update, latest_version, url = self.check_for_updates()
        
        if has_update:
            print(f"\n{Fore.GREEN}✨ Nova versão disponível: {latest_version} (Atual: {self.current_version}){Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Deseja abrir a página de download? (S/N){Style.RESET_ALL}")
            choice = input().strip().lower()
            if choice == 's':
                webbrowser.open(url)
                print(f"{Fore.CYAN}Abrindo navegador...{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}Sistema atualizado ({self.current_version}).{Style.RESET_ALL}\n")

if __name__ == "__main__":
    checker = UpdateChecker()
    checker.prompt_update()
