import pandas as pd
import re
from foton_system.core.config import Config
from foton_system.core.logger import setup_logger
from foton_system.modules.clients.repository import ClientRepository

logger = setup_logger()
config = Config()

class ClientService:
    def __init__(self):
        self.repository = ClientRepository()

    def sync_clients_db_from_folders(self):
        """Updates DB with clients found in folders but not in DB."""
        logger.info("Sincronizando base de clientes a partir das pastas...")
        try:
            db_clients = self.repository.get_clients_dataframe()
            existing_aliases = set(db_clients['Alias'].dropna().unique())
            folder_aliases = self.repository.list_client_folders()
            
            new_aliases = folder_aliases - existing_aliases
            
            if not new_aliases:
                logger.info("Nenhum cliente novo encontrado nas pastas.")
                return

            new_data = pd.DataFrame({'Alias': list(new_aliases)})
            # Generate codes for new clients found in folders? 
            # Original code just added them. We might want to generate codes.
            # For now, following original logic of just adding.
            
            updated_df = pd.concat([db_clients, new_data], ignore_index=True)
            self.repository.save_clients(updated_df)
            logger.info(f"{len(new_aliases)} novos clientes adicionados à base.")
            
        except Exception as e:
            logger.error(f"Erro na sincronização de clientes (DB <- Pastas): {e}")

    def sync_client_folders_from_db(self):
        """Creates folders for clients in DB that don't have folders."""
        logger.info("Sincronizando pastas de clientes a partir da base...")
        try:
            db_clients = self.repository.get_clients_dataframe()
            existing_aliases = set(db_clients['Alias'].dropna().unique())
            folder_aliases = self.repository.list_client_folders()
            
            missing_folders = existing_aliases - folder_aliases
            
            if not missing_folders:
                logger.info("Todas as pastas de clientes já existem.")
                return

            for alias in missing_folders:
                self.repository.create_folder(self.repository.base_pasta / alias)
            
            logger.info(f"{len(missing_folders)} pastas de clientes criadas.")

        except Exception as e:
            logger.error(f"Erro na sincronização de clientes (Pastas <- DB): {e}")

    def sync_services_db_from_folders(self):
        """Updates DB with services found in folders but not in DB."""
        logger.info("Sincronizando base de serviços a partir das pastas...")
        try:
            db_services = self.repository.get_services_dataframe()
            # Group by client to check existence
            registered_services = db_services.groupby('AliasCliente')['Alias'].apply(set).to_dict()
            
            folder_clients = self.repository.list_client_folders()
            new_services_list = []
            ignored = set(config.ignored_folders)

            for client in folder_clients:
                client_services = self.repository.list_service_folders(client)
                known_services = registered_services.get(client, set())
                
                # Filter ignored folders
                actual_services = {s for s in client_services if s not in ignored}
                
                missing_in_db = actual_services - known_services
                
                for service in missing_in_db:
                    new_services_list.append({'AliasCliente': client, 'Alias': service})

            if not new_services_list:
                logger.info("Nenhum serviço novo encontrado nas pastas.")
                return

            new_df = pd.DataFrame(new_services_list)
            updated_df = pd.concat([db_services, new_df], ignore_index=True)
            self.repository.save_services(updated_df)
            logger.info(f"{len(new_services_list)} novos serviços adicionados à base.")

        except Exception as e:
            logger.error(f"Erro na sincronização de serviços (DB <- Pastas): {e}")

    def sync_service_folders_from_db(self):
        """Creates folders for services in DB that don't have folders."""
        logger.info("Sincronizando pastas de serviços a partir da base...")
        try:
            db_services = self.repository.get_services_dataframe()
            folder_clients = self.repository.list_client_folders()
            
            count = 0
            for index, row in db_services.iterrows():
                client = row['AliasCliente']
                service = row['Alias']
                
                if pd.isna(client) or pd.isna(service):
                    continue
                
                # Check if client folder exists first
                if client not in folder_clients:
                    # Optionally create client folder here, but usually handled by client sync
                    continue

                service_path = self.repository.base_pasta / client / service
                if not service_path.exists():
                    self.repository.create_folder(service_path)
                    count += 1
            
            if count == 0:
                logger.info("Todas as pastas de serviços já existem.")
            else:
                logger.info(f"{count} pastas de serviços criadas.")

        except Exception as e:
            logger.error(f"Erro na sincronização de serviços (Pastas <- DB): {e}")

    def generate_client_code(self, name):
        """Generates a unique code for a client."""
        if not name:
            return None
        
        try:
            db_clients = self.repository.get_clients_dataframe()
            existing_codes = set(db_clients['CodCliente'].dropna().values)
        except:
            existing_codes = set()

        parts = name.split()
        if len(parts) > 2:
            base_code = (parts[0][:2] + parts[-1][:2]).upper()
        else:
            base_code = ''.join(filter(str.isalnum, name[:4].upper()))

        code = base_code
        counter = 1
        while code in existing_codes:
            code = f"{base_code}{counter:02d}"
            counter += 1
        
        return code

    def create_client(self, data):
        """Adds a new client to the database."""
        try:
            db_clients = self.repository.get_clients_dataframe()
            
            # Generate code if not provided
            if 'CodCliente' not in data or not data['CodCliente']:
                data['CodCliente'] = self.generate_client_code(data.get('NomeCliente', ''))

            new_row = pd.DataFrame([data])
            updated_df = pd.concat([db_clients, new_row], ignore_index=True)
            
            # Format columns
            updated_df = self._format_columns(updated_df)
            
            self.repository.save_clients(updated_df)
            logger.info(f"Cliente {data.get('NomeCliente')} criado com sucesso.")
            return data
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}")
            raise

    def _format_columns(self, df):
        """Formats specific columns like Data, CPF, CNPJ."""
        for idx, row in df.iterrows():
            if 'DataServico' in row and pd.notna(row['DataServico']):
                df.at[idx, 'DataServico'] = self._format_date(row['DataServico'])
            if 'CPF' in row and pd.notna(row['CPF']):
                df.at[idx, 'CPF'] = self._format_cpf_cnpj(row['CPF'])
            if 'CNPJ' in row and pd.notna(row['CNPJ']):
                df.at[idx, 'CNPJ'] = self._format_cpf_cnpj(row['CNPJ'])
        return df

    def _format_date(self, date_val):
        try:
            return pd.to_datetime(date_val, format='%d-%m-%Y').strftime('%Y-%m-%d')
        except:
            return date_val

    def _format_cpf_cnpj(self, val):
        return ''.join(re.findall(r'\d+', str(val)))
