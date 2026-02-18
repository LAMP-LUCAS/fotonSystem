"""
Deployment Manager: Gerencia inicialização e manutenção da base de dados.

Responsabilidades:
- Criar/resetar estrutura do banco de dados
- Validar integridade
- Gerenciar backup e recuperação
- Ser chamado durante bootstrap e manutenção
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()


class DeploymentManager:
    """Gerencia a inicialização e manutenção do ambiente do FotonSystem."""

    # Estrutura esperada da base de dados
    BASE_SCHEMA = {
        "baseClientes": [
            "ID", "NomeCliente", "Alias", "TelefoneCliente", "Email",
            "CPF_CNPJ", "Endereco", "CidadeProposta", "EstadoCivil", "Profissao"
        ],
        "baseServicos": [
            "ID", "AliasCliente", "Alias", "CodServico", "Modalidade", "Ano",
            "Demanda", "AreaTotal", "AreaCoberta", "AreaDescoberta",
            "Detalhes", "Estilo", "Ambientes", "ValorProposta", "ValorContrato"
        ]
    }

    def __init__(self):
        self.config = Config()
        self.db_path = self.config.base_dados
        self.pasta_clientes = self.config.base_pasta_clientes

    def print_header(self, title):
        """Imprime um cabeçalho formatado."""
        sep = "=" * 70
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{sep}")
        print(f"{title.center(70)}")
        print(f"{sep}{Style.RESET_ALL}\n")

    def print_success(self, msg):
        print(f"{Fore.GREEN}✔ {msg}{Style.RESET_ALL}")

    def print_error(self, msg):
        print(f"{Fore.RED}✘ {msg}{Style.RESET_ALL}")

    def print_warning(self, msg):
        print(f"{Fore.YELLOW}⚠ {msg}{Style.RESET_ALL}")

    def print_info(self, msg):
        print(f"{Fore.CYAN}ℹ {msg}{Style.RESET_ALL}")

    # ==================== VALIDAÇÃO ====================

    def validate_database(self):
        """Valida se o banco de dados existe e tem a estrutura correta."""
        self.print_header("VALIDAÇÃO DE BASE DE DADOS")

        if not self.db_path.exists():
            self.print_error(f"Arquivo não encontrado: {self.db_path}")
            return False

        try:
            # Verifica abas
            excel_file = pd.ExcelFile(self.db_path)
            sheet_names = set(excel_file.sheet_names)
            expected_sheets = set(self.BASE_SCHEMA.keys())

            if not expected_sheets.issubset(sheet_names):
                missing = expected_sheets - sheet_names
                self.print_error(f"Abas faltando: {missing}")
                return False

            # Verifica colunas em cada aba
            for sheet, expected_cols in self.BASE_SCHEMA.items():
                df = pd.read_excel(self.db_path, sheet_name=sheet)
                actual_cols = set(df.columns)
                missing_cols = set(expected_cols) - actual_cols

                if missing_cols:
                    self.print_warning(f"Colunas faltando em '{sheet}': {missing_cols}")
                else:
                    self.print_success(f"Aba '{sheet}': {len(df)} registros, colunas OK")

            return True

        except Exception as e:
            self.print_error(f"Erro ao validar: {e}")
            logger.error(f"Database validation error: {e}", exc_info=True)
            return False

    # ==================== CRIAÇÃO ====================

    def create_database(self, force=False):
        """
        Cria a base de dados com a estrutura completa.
        
        Args:
            force: Se True, sobrescreve arquivo existente
        
        Returns:
            bool: True se sucesso
        """
        self.print_header("CRIANDO NOVA BASE DE DADOS")

        if self.db_path.exists() and not force:
            self.print_warning(f"Arquivo já existe: {self.db_path}")
            response = input(f"{Fore.YELLOW}Deseja sobrescrever? (s/n): {Style.RESET_ALL}").strip().lower()
            if response != 's':
                self.print_info("Operação cancelada.")
                return False

        try:
            # Cria diretório se necessário
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Cria backup do arquivo anterior se existir
            if self.db_path.exists():
                backup_path = self._create_backup(self.db_path)
                self.print_info(f"Backup criado: {backup_path}")

            # Cria arquivo Excel com múltiplas abas
            with pd.ExcelWriter(self.db_path, engine='openpyxl') as writer:
                for sheet_name, columns in self.BASE_SCHEMA.items():
                    df = pd.DataFrame(columns=columns)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    self.print_info(f"Aba criada: '{sheet_name}' com {len(columns)} colunas")

            # Valida o resultado
            if self.validate_database():
                self.print_success(f"Base de dados criada com sucesso!")
                self.print_info(f"Localização: {self.db_path}")
                return True
            else:
                self.print_error("Validação falhou após criação.")
                return False

        except Exception as e:
            self.print_error(f"Erro ao criar base: {e}")
            logger.error(f"Database creation error: {e}", exc_info=True)
            return False

    def repair_database(self):
        """
        Tenta reparar uma base de dados corrompida/incompleta.
        Mantém os dados existentes e adiciona abas/colunas faltando.
        """
        self.print_header("REPARANDO BASE DE DADOS")

        if not self.db_path.exists():
            self.print_error(f"Arquivo não encontrado: {self.db_path}")
            return False

        try:
            excel_file = pd.ExcelFile(self.db_path)
            current_sheets = set(excel_file.sheet_names)
            expected_sheets = set(self.BASE_SCHEMA.keys())

            repaired = False

            # Adiciona abas faltando
            missing_sheets = expected_sheets - current_sheets
            if missing_sheets:
                with pd.ExcelWriter(self.db_path, engine='openpyxl', mode='a') as writer:
                    for sheet in missing_sheets:
                        df = pd.DataFrame(columns=self.BASE_SCHEMA[sheet])
                        df.to_excel(writer, sheet_name=sheet, index=False)
                        self.print_info(f"Aba adicionada: '{sheet}'")
                        repaired = True

            # Adiciona colunas faltando em cada aba
            for sheet, expected_cols in self.BASE_SCHEMA.items():
                if sheet in current_sheets:
                    df = pd.read_excel(self.db_path, sheet_name=sheet)
                    missing_cols = set(expected_cols) - set(df.columns)

                    if missing_cols:
                        for col in missing_cols:
                            df[col] = None
                        
                        # Salva com as novas colunas
                        with pd.ExcelWriter(self.db_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                            df.to_excel(writer, sheet_name=sheet, index=False)
                        
                        self.print_info(f"Colunas adicionadas a '{sheet}': {missing_cols}")
                        repaired = True

            if repaired:
                self.print_success("Base de dados reparada!")
                return self.validate_database()
            else:
                self.print_success("Base de dados já está íntegra.")
                return True

        except Exception as e:
            self.print_error(f"Erro ao reparar: {e}")
            logger.error(f"Database repair error: {e}", exc_info=True)
            return False

    # ==================== BACKUP ====================

    def _create_backup(self, source_path: Path) -> Path:
        """Cria um backup do arquivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = source_path.parent / f"BKP-baseDados_{timestamp}.xlsx"
        
        try:
            import shutil
            shutil.copy2(source_path, backup_path)
            return backup_path
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return None

    def list_backups(self):
        """Lista todos os backups disponíveis."""
        self.print_header("BACKUPS DISPONÍVEIS")

        backup_dir = self.db_path.parent
        backups = sorted(
            backup_dir.glob("BKP-baseDados_*.xlsx"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if not backups:
            self.print_warning("Nenhum backup encontrado.")
            return []

        for i, backup in enumerate(backups[:10], 1):  # Mostra últimos 10
            size_mb = backup.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"{i}. {backup.name} ({size_mb:.2f} MB) - {mtime.strftime('%d/%m/%Y %H:%M')}")

        return backups

    def restore_backup(self, backup_index=None):
        """Restaura um backup."""
        self.print_header("RESTAURAR DE BACKUP")

        backups = self.list_backups()
        if not backups:
            return False

        if backup_index is None:
            try:
                backup_index = int(input(f"\n{Fore.CYAN}Escolha o número do backup: {Style.RESET_ALL}")) - 1
                if not (0 <= backup_index < len(backups)):
                    self.print_error("Índice inválido.")
                    return False
            except ValueError:
                self.print_error("Entrada inválida.")
                return False

        backup_path = backups[backup_index]

        try:
            # Cria backup da versão atual
            if self.db_path.exists():
                self._create_backup(self.db_path)

            # Restaura
            import shutil
            shutil.copy2(backup_path, self.db_path)
            self.print_success(f"Restaurado de: {backup_path.name}")
            return True

        except Exception as e:
            self.print_error(f"Erro ao restaurar: {e}")
            logger.error(f"Restore error: {e}", exc_info=True)
            return False

    # ==================== MENU INTERATIVO ====================

    def interactive_menu(self):
        """Menu interativo para o usuário."""
        while True:
            self.print_header("GERENCIADOR DE DEPLOYMENT")
            print(f"{Fore.YELLOW}Localização da Base: {Fore.WHITE}{self.db_path}\n")
            
            options = [
                ("1", "Validar Base de Dados"),
                ("2", "Criar Nova Base (com confirmação)"),
                ("3", "Reparar Base Existente"),
                ("4", "Listar Backups"),
                ("5", "Restaurar de Backup"),
                ("0", "Sair")
            ]

            for key, label in options:
                print(f"{Fore.CYAN}{key}. {Fore.WHITE}{label}")

            choice = input(f"\n{Fore.CYAN}>> Escolha: {Style.RESET_ALL}").strip()

            if choice == "1":
                self.validate_database()
            elif choice == "2":
                if self.create_database(force=False):
                    input(f"\n{Fore.GREEN}Pressione ENTER para continuar...{Style.RESET_ALL}")
            elif choice == "3":
                if self.repair_database():
                    input(f"\n{Fore.GREEN}Pressione ENTER para continuar...{Style.RESET_ALL}")
            elif choice == "4":
                self.list_backups()
            elif choice == "5":
                if self.restore_backup():
                    input(f"\n{Fore.GREEN}Pressione ENTER para continuar...{Style.RESET_ALL}")
            elif choice == "0":
                self.print_info("Saindo...")
                break
            else:
                self.print_error("Opção inválida.")

            print("\n")


def main():
    """Ponto de entrada para execução direta."""
    manager = DeploymentManager()
    manager.interactive_menu()


if __name__ == "__main__":
    main()
