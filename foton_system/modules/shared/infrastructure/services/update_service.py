import requests
from foton_system import __version__
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()

class UpdateChecker:
    GITHUB_API_URL = "https://api.github.com/repos/LAMP-LUCAS/fotonSystem/releases/latest"

    @staticmethod
    def check_for_updates():
        """
        Verifica se existe uma nova versão disponível no GitHub.
        Retorna (tem_update, versao_recente, url_download)
        """
        try:
            logger.info("Verificando se há atualizações...")
            response = requests.get(UpdateChecker.GITHUB_API_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").replace("v", "")
                download_url = data.get("html_url", "")

                if latest_version and latest_version > __version__:
                    logger.info(f"Nova versão encontrada: {latest_version} (Versão atual: {__version__})")
                    return True, latest_version, download_url
                else:
                    logger.info("O sistema está atualizado.")
            else:
                logger.warning(f"Não foi possível verificar atualizações. Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Erro ao verificar atualizações: {e}")
        
        return False, __version__, ""
