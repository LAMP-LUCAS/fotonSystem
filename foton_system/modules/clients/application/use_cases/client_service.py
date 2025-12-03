import pandas as pd
import re
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort

from foton_system.modules.shared.infrastructure.validators import validate_filename

logger = setup_logger()
class ClientService:
    def __init__(self, repository: ClientRepositoryPort):
        self.repository = repository

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

            # Access base_pasta from repository if possible, or config
            # Since repository abstracts storage, we should ask repository to create folder by name/path
            # But repository.create_folder takes a path.
            # We need to know the base path.
            # The port doesn't expose base_pasta.
            # We can assume the repository knows how to handle it if we pass a relative path or name?
            # Or we should add `get_base_path` to port?
            # For now, let's use config since it's shared, or assume repository handles full paths.
            # The original code used self.repository.base_pasta / alias.
            # Let's use Config().base_pasta_clientes / alias.
            
            for alias in missing_folders:
                self.repository.create_folder(Config().base_pasta_clientes / alias)
            
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
            ignored = set(Config().ignored_folders)

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

    def sync_service_folders_from_db(self, client_alias=None):
        """Creates folders for services in DB that don't have folders."""
        logger.info(f"Sincronizando pastas de serviços a partir da base... {'(Cliente: ' + client_alias + ')' if client_alias else '(Todos)'}")
        try:
            db_services = self.repository.get_services_dataframe()
            if client_alias:
                # Filter DB services by client
                db_services = db_services[db_services['AliasCliente'] == client_alias]
                
            folder_clients = self.repository.list_client_folders()
            
            count = 0
            for index, row in db_services.iterrows():
                client = row['AliasCliente']
                service = row['Alias']
                
                if pd.isna(client) or pd.isna(service):
                    continue
                
                if client not in folder_clients:
                    continue

                service_path = Config().base_pasta_clientes / client / service
                # We need to check existence. Repository doesn't have exists() method exposed directly for arbitrary paths?
                # We can use os.path.exists or Path.exists since we are using local file system.
                # But to be pure, we should ask repository.
                # For now, using Path.exists is pragmatic as we are in Hybrid mode.
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
            # Validation
            if not validate_filename(data.get('NomeCliente', '')):
                raise ValueError("Nome do cliente contém caracteres inválidos ou é reservado.")
            if not validate_filename(data.get('Alias', '')):
                raise ValueError("Alias do cliente contém caracteres inválidos ou é reservado.")

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

    # --- Distributed Database (File Sync) ---

    def _generate_service_code(self, client_alias, service_alias):
        """Generates a unique code for a service."""
        # Simple generation: 3 letters of client + 3 letters of service + 01
        base = (client_alias[:3] + service_alias[:3]).upper()
        base = ''.join(filter(str.isalnum, base))
        return f"{base}01" # Simplified for now, could check DB for collisions

    def _generate_filename(self, cod, alias, ver="00", rev="R00"):
        """Generates filename: COD_DOC_CD_VER_REV_INFO-ALIAS.md"""
        return f"{cod}_DOC_CD_{ver}_{rev}_INFO-{alias}.md"

    def _parse_filename(self, filename):
        """Extracts VER and REV from filename."""
        # Expected: COD_DOC_CD_VER_REV_INFO-ALIAS.md
        try:
            parts = filename.stem.split('_')
            if len(parts) >= 6:
                return parts[3], parts[4] # VER, REV
        except:
            pass
        return "00", "R00"

    def _get_latest_file(self, folder, alias):
        """Finds the latest version file for the alias in the folder."""
        if not folder.exists():
            return None
        
        files = list(folder.glob(f"*_INFO-{alias}.md"))
        if not files:
            return None
        
        # Sort by name (which effectively sorts by VER and REV if format is consistent)
        # Better: Parse and sort
        def sort_key(f):
            ver, rev = self._parse_filename(f)
            return (ver, rev)
        
        files.sort(key=sort_key, reverse=True)
        return files[0]

    def _read_file_content(self, path):
        """Reads key-value pairs from MD file."""
        data = {}
        if not path.exists():
            return data
            
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip()
        return data

    # --- Templates ---
    
    CLIENT_TEMPLATE_STR = """## INFO-CLIENTE.md
Aqui tem todas as colunas da tabela de clientes e variáveis extra para personalização

### DADOS DO CLIENTE - PROPOSTA

Dados que serão utilizados nas propostas comerciais:

@dataProposta: 
@numeroProposta: 
@nomeProposta: 
@cidadeProposta: 
@localProposta: 
@geolocalizacaoProposta: 
@nomeCliente: 
@empregoCliente: 
@estadoCivilCliente: 
@cpfCnpjCliente: 
@enderecoCliente: 
"""

    SERVICE_TEMPLATE_STR = """## INFO-SERVICO.md

@TEMPLATE: 

### DADOS BÁSICOS

@DataAtual: 

### DADOS DO CLIENTE - CONTRATO

O cliente pode precisar utilizar dados distintos no contrato, portanto abaixo tem os dados para a contratação do serviço:

@nomeContrato: 
@numeroContrato: 
@nomeClienteContrato: 
@estadoCivilClienteContrato: 
@empregoClienteContrato: 
@telefoneClienteContrato: 
@emailClienteContrato: 
@enderecoClienteContrato: 
@cpfCnpjClienteContrato: 

### DADOS DO SERVIÇO

@modalidadeServico: 
@anoProjeto: 
@demandaProposta: 
@areaTotal: 
@areaCoberta: 
@areaDescoberta: 
@detalhesProposta: 
@estiloProjeto: 
@ambientesProjeto: 
@inProposta: 
@lvProposta: 
@anProposta: 
@baProposta: 
@prProposta: 
@inSolucao: 
@valorProposta: 
@valorContrato: 

#### DADOS PARA ESTIMATIVA DE CUSTO - PROPOSTA

@projArqEng: 
@procLegais: 
@ACEqv: 
@execcub: 
@execInfra: 
@execPais: 
@execMob: 
@totalParcial: 
@totalExec: 
@totalinss: 
@totalGeral: 
@ArqEng%: 
@Legais%: 
@precoCUB%: 
@Parcial%: 
@infra%: 
@pais%: 
@mob%: 
@Exec%: 
@inss%: 
"""

    def _write_formatted_file_content(self, path, data, template_str):
        """
        Writes data to file using the template structure.
        Preserves existing values if not in data (for updates).
        """
        lines = template_str.split('\n')
        output_lines = []
        
        # Track which keys we've written to avoid duplication
        written_keys = set()
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('@') and ':' in stripped:
                key = stripped.split(':')[0].strip()
                written_keys.add(key)
                
                # Value priority: Data (DB) > Existing File > Empty
                value = data.get(key, "")
                output_lines.append(f"{key}: {value}")
            else:
                output_lines.append(line)
        
        # Append extra keys from data that were not in template
        extra_keys = [k for k in data.keys() if k not in written_keys and k.startswith('@')]
        if extra_keys:
            output_lines.append("\n### VARIÁVEIS EXTRAS")
            for key in extra_keys:
                output_lines.append(f"{key}: {data[key]}")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))

    def export_client_data(self):
        """Exports DB client data to MD files in client folders."""
        logger.info("Exporting client data to files...")
        count = 0
        try:
            df = self.repository.get_clients_dataframe()
            latest_df = df.groupby('Alias').last().reset_index()

            for _, row in latest_df.iterrows():
                alias = row['Alias']
                cod = row.get('CodCliente')
                if not cod:
                    cod = self.generate_client_code(row.get('NomeCliente'))
                
                folder = Config().base_pasta_clientes / alias
                if not folder.exists():
                    continue

                # Prepare data for file (Map DB columns to Variables)
                # Assuming DB columns match variable names or we map them here
                # For now, we use the row dict directly, but we might need mapping if DB cols differ
                file_data = row.dropna().to_dict()
                
                # Check existing file to preserve extra data
                latest_file = self._get_latest_file(folder, alias)
                
                should_create = False
                ver, rev = "00", "R00"
                existing_data = {}
                
                if latest_file:
                    existing_data = self._read_file_content(latest_file)
                    # Merge: DB overrides existing for shared keys, keep existing for others
                    merged_data = {**existing_data, **file_data}
                    
                    # Check difference
                    is_different = False
                    for k, v in merged_data.items():
                        if str(v) != existing_data.get(k):
                            is_different = True
                            break
                    
                    if is_different:
                        should_create = True
                        ver, rev = self._parse_filename(latest_file)
                        rev = self._increment_revision(rev)
                    
                    file_data = merged_data # Use merged data for writing
                else:
                    should_create = True

                if should_create:
                    filename = self._generate_filename(cod, alias, ver, rev)
                    self._write_formatted_file_content(folder / filename, file_data, self.CLIENT_TEMPLATE_STR)
                    count += 1

            logger.info(f"{count} arquivos de cliente exportados/atualizados.")

        except Exception as e:
            logger.error(f"Erro ao exportar dados de clientes: {e}")

    def export_service_data(self):
        """Exports DB service data to MD files in service folders."""
        logger.info("Exporting service data to files...")
        count = 0
        try:
            df = self.repository.get_services_dataframe()
            latest_df = df.groupby(['AliasCliente', 'Alias']).last().reset_index()

            for _, row in latest_df.iterrows():
                client_alias = row['AliasCliente']
                service_alias = row['Alias']
                
                cod = row.get('CodServico')
                if not cod or pd.isna(cod):
                    cod = self._generate_service_code(client_alias, service_alias)
                
                folder = Config().base_pasta_clientes / client_alias / service_alias
                if not folder.exists():
                    continue

                file_data = row.dropna().to_dict()
                file_data['CodServico'] = cod
                
                latest_file = self._get_latest_file(folder, service_alias)
                
                should_create = False
                ver, rev = "00", "R00"
                existing_data = {}
                
                if latest_file:
                    existing_data = self._read_file_content(latest_file)
                    merged_data = {**existing_data, **file_data}
                    
                    is_different = False
                    for k, v in merged_data.items():
                        if str(v) != existing_data.get(k):
                            is_different = True
                            break
                    
                    if is_different:
                        should_create = True
                        ver, rev = self._parse_filename(latest_file)
                        rev = self._increment_revision(rev)
                    
                    file_data = merged_data
                else:
                    should_create = True

                if should_create:
                    filename = self._generate_filename(cod, service_alias, ver, rev)
                    self._write_formatted_file_content(folder / filename, file_data, self.SERVICE_TEMPLATE_STR)
                    count += 1

            logger.info(f"{count} arquivos de serviço exportados/atualizados.")

        except Exception as e:
            logger.error(f"Erro ao exportar dados de serviços: {e}")

    def import_service_data(self):
        """Imports data from MD files to DB (Services)."""
        logger.info("Importing service data from files...")
        count = 0
        try:
            df = self.repository.get_services_dataframe()
            folder_clients = self.repository.list_client_folders()
            
            new_rows = []
            
            for client_alias in folder_clients:
                service_folders = self.repository.list_service_folders(client_alias)
                for service_alias in service_folders:
                    folder = Config().base_pasta_clientes / client_alias / service_alias
                    latest_file = self._get_latest_file(folder, service_alias)
                    
                    if not latest_file:
                        continue
                    
                    file_data = self._read_file_content(latest_file)
                    if not file_data:
                        continue

                    # Compare with DB
                    db_entry = df[(df['AliasCliente'] == client_alias) & (df['Alias'] == service_alias)]
                    if not db_entry.empty:
                        last_db_row = db_entry.iloc[-1]
                        is_different = False
                        for k, v in file_data.items():
                            if k in last_db_row and str(last_db_row[k]) != str(v):
                                is_different = True
                                break
                            if k not in last_db_row:
                                is_different = True
                                break
                        
                        if not is_different:
                            continue

                    file_data['DataAtualizacao'] = pd.Timestamp.now()
                    # Ensure keys
                    file_data['AliasCliente'] = client_alias
                    file_data['Alias'] = service_alias
                    
                    new_rows.append(file_data)
                    count += 1

            if new_rows:
                new_df = pd.DataFrame(new_rows)
                updated_df = pd.concat([df, new_df], ignore_index=True)
                self.repository.save_services(updated_df)
                logger.info(f"{count} registros de serviço importados/atualizados.")
            else:
                logger.info("Nenhuma alteração encontrada nos arquivos de serviço.")

        except Exception as e:
            logger.error(f"Erro ao importar dados de serviços: {e}")
