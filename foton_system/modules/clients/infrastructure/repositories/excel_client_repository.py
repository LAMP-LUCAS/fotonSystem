import pandas as pd
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort
from foton_system.modules.shared.domain.exceptions import (
    DatabaseLockError,
    DatabaseConnectionError
)

logger = setup_logger()


def retry_with_backoff(max_retries: int = 3, base_delay: float = 0.5):
    """
    Decorator that retries a function with exponential backoff.
    Useful for file operations that may fail due to temporary locks.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except PermissionError as e:
                    last_exception = e
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Tentativa {attempt + 1}/{max_retries} falhou (arquivo bloqueado). Aguardando {delay:.1f}s...")
                    time.sleep(delay)
                except Exception as e:
                    raise
            # All retries failed
            raise DatabaseLockError(str(args[0].base_dados if hasattr(args[0], 'base_dados') else 'unknown'))
        return wrapper
    return decorator


class ExcelClientRepository(ClientRepositoryPort):
    """
    Excel-based implementation of ClientRepositoryPort.
    
    Features:
    - In-memory caching for read operations
    - Retry with exponential backoff for write operations
    - Smart backup strategy
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize repository with optional config injection.
        
        Args:
            config: Configuration object. If None, uses default Config singleton.
        """
        self._config = config or Config()
        
        # Cache for read operations
        self._clients_cache: Optional[pd.DataFrame] = None
        self._services_cache: Optional[pd.DataFrame] = None
        self._cache_valid = False

    def _invalidate_cache(self):
        """Invalidates the cache, forcing next read to reload from disk."""
        self._cache_valid = False
        self._clients_cache = None
        self._services_cache = None

    @property
    def base_pasta(self):
        return self._config.base_pasta_clientes

    @property
    def base_dados(self):
        return self._config.base_dados

    def check_files(self):
        if not self.base_dados.exists():
            raise FileNotFoundError(f"Base de dados não encontrada: {self.base_dados}")
        if not self.base_pasta.exists():
            raise FileNotFoundError(f"Pasta de clientes não encontrada: {self.base_pasta}")

    def _ensure_database_exists(self):
        """
        Garante que a base de dados existe e tem a estrutura correta.
        Se o arquivo não existir, cria com a estrutura padrão.
        """
        if not self.base_dados.exists():
            # Cria diretório se necessário
            self.base_dados.parent.mkdir(parents=True, exist_ok=True)
            
            # Cria arquivo Excel com as abas padrão
            logger.warning(f"Base de dados não encontrada. Criando em: {self.base_dados}")
            
            with pd.ExcelWriter(self.base_dados, engine='openpyxl') as writer:
                # Aba de Clientes
                df_clientes = pd.DataFrame(columns=[
                    'ID', 'NomeCliente', 'Alias', 'TelefoneCliente', 'Email',
                    'CPF_CNPJ', 'Endereco', 'CidadeProposta', 'EstadoCivil', 'Profissao'
                ])
                df_clientes.to_excel(writer, sheet_name='baseClientes', index=False)
                
                # Aba de Serviços
                df_servicos = pd.DataFrame(columns=[
                    'ID', 'AliasCliente', 'Alias', 'CodServico', 'Modalidade', 'Ano',
                    'Demanda', 'AreaTotal', 'AreaCoberta', 'AreaDescoberta',
                    'Detalhes', 'Estilo', 'Ambientes', 'ValorProposta', 'ValorContrato'
                ])
                df_servicos.to_excel(writer, sheet_name='baseServicos', index=False)
            
            logger.info(f"Base de dados criada com sucesso em: {self.base_dados}")

    def _create_smart_backup(self):
        """
        Cria backup apenas se a base foi significativamente modificada.
        Usa estratégia inteligente para não encher o HD.
        
        Não cria backup se:
        - Já existe um backup nas últimas 30 minutos E tamanho do arquivo não mudou muito
        - Arquivo não foi modificado
        """
        if not self.base_dados.exists():
            return
        
        try:
            backup_dir = self.base_dados.parent
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"BKP-baseDados_{timestamp}.xlsx"
            
            # Verifica se deve criar backup
            current_size = self.base_dados.stat().st_size
            
            # Procura backup mais recente
            recent_backups = sorted(
                backup_dir.glob("BKP-baseDados_*.xlsx"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            if recent_backups:
                latest_backup = recent_backups[0]
                latest_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
                time_diff = datetime.now() - latest_time
                
                # Se backup foi feito há menos de 30 minutos E tamanho mudou menos de 10%
                if time_diff < timedelta(minutes=30):
                    size_diff_percent = abs(current_size - latest_backup.stat().st_size) / latest_backup.stat().st_size * 100
                    
                    if size_diff_percent < 10:
                        logger.debug(f"Backup recente existe (há {time_diff.seconds//60}min). Pulando backup.")
                        
                        # Mas faz limpeza se necessário
                        self._cleanup_old_backups()
                        return
            
            # Se passou pelas verificações, cria o backup
            import shutil
            shutil.copy2(self.base_dados, backup_path)
            logger.debug(f"Backup criado: {backup_path.name}")
            
            # Aplica limpeza de backups antigos
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.warning(f"Erro ao criar backup inteligente: {e}")

    def _cleanup_old_backups(self):
        """
        Remove backups antigos segundo política de retenção.
        
        Política:
        - Últimas 24h: máximo 1 backup por hora
        - Últimos 7 dias: máximo 1 backup por dia
        - Últimas 4 semanas: máximo 1 backup por semana
        - Últimos 3 meses: máximo 1 backup por mês
        - Mais antigo: deleta
        - Máximo total: 500 MB
        """
        backup_dir = self.base_dados.parent
        all_backups = sorted(
            backup_dir.glob("BKP-baseDados_*.xlsx"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not all_backups:
            return
        
        # Aplica política de retenção
        to_keep = set()
        to_keep.add(all_backups[0])  # Sempre manter o mais recente
        
        for backup in all_backups[1:]:
            backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
            age = datetime.now() - backup_time
            
            should_keep = False
            
            # Últimas 24h: 1 por hora
            if age < timedelta(hours=24):
                hour_str = backup_time.strftime("%Y%m%d_%H")
                if not any(
                    datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y%m%d_%H") == hour_str
                    for b in to_keep
                ):
                    should_keep = True
            
            # Últimos 7 dias: 1 por dia
            elif age < timedelta(days=7):
                day_str = backup_time.strftime("%Y%m%d")
                if not any(
                    datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y%m%d") == day_str
                    for b in to_keep
                ):
                    should_keep = True
            
            # Últimas 4 semanas: 1 por semana
            elif age < timedelta(weeks=4):
                week_str = backup_time.strftime("%Y-W%W")
                if not any(
                    datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-W%W") == week_str
                    for b in to_keep
                ):
                    should_keep = True
            
            # Últimos 3 meses: 1 por mês
            elif age < timedelta(days=90):
                month_str = backup_time.strftime("%Y%m")
                if not any(
                    datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y%m") == month_str
                    for b in to_keep
                ):
                    should_keep = True
            
            if should_keep:
                to_keep.add(backup)
        
        # Remove backups que não devem ser mantidos
        deleted_count = 0
        for backup in all_backups:
            if backup not in to_keep:
                try:
                    backup.unlink()
                    deleted_count += 1
                    logger.debug(f"Backup antigo deletado: {backup.name}")
                except Exception as e:
                    logger.warning(f"Erro ao deletar backup {backup.name}: {e}")
        
        # Verifica limite de tamanho total (máximo 500 MB)
        total_size = sum(b.stat().st_size for b in to_keep) / (1024 * 1024)
        if total_size > 500:
            # Remove dos mais antigos mantidos
            to_delete = sorted(to_keep - {all_backups[0]}, key=lambda x: x.stat().st_mtime)
            for backup in to_delete:
                try:
                    backup_size = backup.stat().st_size / (1024 * 1024)
                    backup.unlink()
                    to_keep.discard(backup)
                    total_size -= backup_size
                    logger.debug(f"Backup deletado (limite de tamanho): {backup.name}")
                    if total_size <= 500:
                        break
                except Exception as e:
                    logger.warning(f"Erro ao deletar backup {backup.name}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Limpeza de backups: {deleted_count} arquivos deletados")

    def get_clients_dataframe(self) -> pd.DataFrame:
        """Get clients DataFrame, using cache if valid."""
        if self._cache_valid and self._clients_cache is not None:
            return self._clients_cache.copy()
        
        try:
            self._ensure_database_exists()
            self._clients_cache = pd.read_excel(self.base_dados, sheet_name='baseClientes')
            self._cache_valid = True
            return self._clients_cache.copy()
        except Exception as e:
            logger.error(f"Erro ao ler base de clientes: {e}")
            raise

    def get_services_dataframe(self) -> pd.DataFrame:
        """Get services DataFrame, using cache if valid."""
        if self._cache_valid and self._services_cache is not None:
            return self._services_cache.copy()
        
        try:
            self._ensure_database_exists()
            self._services_cache = pd.read_excel(self.base_dados, sheet_name='baseServicos')
            self._cache_valid = True
            return self._services_cache.copy()
        except Exception as e:
            logger.error(f"Erro ao ler base de serviços: {e}")
            raise

    def list_client_folders(self) -> set:
        return {pasta.name for pasta in self.base_pasta.iterdir() if pasta.is_dir()}

    def list_service_folders(self, client_name: str) -> set:
        client_path = self.base_pasta / client_name
        if client_path.exists() and client_path.is_dir():
            return {pasta.name for pasta in client_path.iterdir() if pasta.is_dir()}
        return set()

    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def save_clients(self, df: pd.DataFrame):
        try:
            self._ensure_database_exists()
            
            # Garante que o arquivo tem estrutura correta antes de salvar
            if self.base_dados.exists():
                # Carrega dados de serviços existentes para preservar na mesclagem
                try:
                    df_servicos = pd.read_excel(self.base_dados, sheet_name='baseServicos')
                except:
                    df_servicos = pd.DataFrame(columns=[
                        'ID', 'AliasCliente', 'Alias', 'CodServico', 'Modalidade', 'Ano',
                        'Demanda', 'AreaTotal', 'AreaCoberta', 'AreaDescoberta',
                        'Detalhes', 'Estilo', 'Ambientes', 'ValorProposta', 'ValorContrato'
                    ])
                
                # Escreve ambas as abas
                with pd.ExcelWriter(self.base_dados, engine="openpyxl", mode='w') as writer:
                    df.to_excel(writer, sheet_name='baseClientes', index=False)
                    df_servicos.to_excel(writer, sheet_name='baseServicos', index=False)
            else:
                # Se arquivo não existe, usa append (que criará)
                with pd.ExcelWriter(self.base_dados, mode='a', engine="openpyxl", if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name='baseClientes', index=False)
            
            # Invalidate cache after write
            self._invalidate_cache()
            
            # Backup inteligente (não enche o HD)
            self._create_smart_backup()
            logger.info(f"Base de clientes salva")
        except DatabaseLockError:
            raise
        except Exception as e:
            logger.error(f"Erro ao salvar base de clientes: {e}")
            raise

    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def save_services(self, df: pd.DataFrame):
        try:
            self._ensure_database_exists()
            
            # Garante que o arquivo tem estrutura correta antes de salvar
            if self.base_dados.exists():
                # Carrega dados de clientes existentes para preservar na mesclagem
                try:
                    df_clientes = pd.read_excel(self.base_dados, sheet_name='baseClientes')
                except:
                    df_clientes = pd.DataFrame(columns=[
                        'ID', 'NomeCliente', 'Alias', 'TelefoneCliente', 'Email',
                        'CPF_CNPJ', 'Endereco', 'CidadeProposta', 'EstadoCivil', 'Profissao'
                    ])
                
                # Escreve ambas as abas
                with pd.ExcelWriter(self.base_dados, engine="openpyxl", mode='w') as writer:
                    df_clientes.to_excel(writer, sheet_name='baseClientes', index=False)
                    df.to_excel(writer, sheet_name='baseServicos', index=False)
            else:
                # Se arquivo não existe, usa append (que criará)
                with pd.ExcelWriter(self.base_dados, mode='a', engine="openpyxl", if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name='baseServicos', index=False)
            
            # Invalidate cache after write
            self._invalidate_cache()
            
            # Backup inteligente (não enche o HD)
            self._create_smart_backup()
            logger.info(f"Base de serviços salva")
        except DatabaseLockError:
            raise
        except Exception as e:
            logger.error(f"Erro ao salvar base de serviços: {e}")
            raise

    def create_folder(self, path: str):
        path = Path(path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Pasta criada: {path}")
        except Exception as e:
            logger.error(f"Erro ao criar pasta {path}: {e}")
            raise
