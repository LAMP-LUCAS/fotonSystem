from pathlib import Path
from typing import Optional

import pandas as pd

from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.shared.infrastructure.validators import validate_filename
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
from foton_system.modules.shared.domain.exceptions import InvalidAliasError, DatabaseLockError, ValidationError
from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name, format_columns
from foton_system.modules.clients.application.use_cases.client_query import resolve_client_path, generate_client_code, list_service_nodes

logger = setup_logger()

CLIENT_TEMPLATE_STR = """## INFO-CLIENTE.md
Aqui tem todas as colunas da tabela de clientes e variáveis extra para personalização

### DADOS DO CLIENTE - PROPOSTA

Dados que serão utilizados nas propostas comerciais:

@dataProposta; 
@numeroProposta; 
@nomeProposta; 
@cidadeProposta; 
@localProposta; 
@geolocalizacaoProposta; 
@nomeCliente; 
@empregoCliente; 
@estadoCivilCliente; 
@cpfCnpjCliente; 
@enderecoCliente; 
"""

SERVICE_TEMPLATE_STR = """## INFO-SERVICO.md

@TEMPLATE; 

### DADOS BÁSICOS

@DataAtual; 

### DADOS DO CLIENTE - CONTRATO

O cliente pode precisar utilizar dados distintos no contrato, portanto abaixo tem os dados para a contratação do serviço:

@nomeContrato; 
@numeroContrato; 
@nomeClienteContrato; 
@estadoCivilClienteContrato; 
@empregoClienteContrato; 
@telefoneClienteContrato; 
@emailClienteContrato; 
@enderecoClienteContrato; 
@cpfCnpjClienteContrato; 

### DADOS DO SERVIÇO

@modalidadeServico; 
@anoProjeto; 
@demandaProposta; 
@areaTotal; 
@areaCoberta; 
@areaDescoberta; 
@detalhesProposta; 
@estiloProjeto; 
@ambientesProjeto; 
@inProposta; 
@lvProposta; 
@anProposta; 
@baProposta; 
@prProposta; 
@inSolucao; 
@valorProposta; 
@valorContrato; 

#### DADOS PARA ESTIMATIVA DE CUSTO - PROPOSTA

@projArqEng; 
@procLegais; 
@ACEqv; 
@execcub; 
@execInfra; 
@execPais; 
@execMob; 
@totalParcial; 
@totalExec; 
@totalinss; 
@totalGeral; 
@ArqEng%; 
@Legais%; 
@precoCUB%; 
@Parcial%; 
@infra%; 
@pais%; 
@mob%; 
@Exec%; 
@inss%; 
"""


def read_client_info_file(client_path: Path) -> dict:
    """Read the content of the most recent INFO file in a client directory.

    Returns {'filename': str, 'content': str}.
    Raises ValueError if no INFO file is found.
    """
    info_files = list(client_path.glob("*INFO*.md"))
    if not info_files:
        raise ValueError(
            f"No INFO file found for '{client_path.name}'.\n"
            f"Expected pattern: *INFO*.md in {client_path}"
        )
    info_file = sorted(info_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
    content = info_file.read_text(encoding="utf-8")
    return {'filename': info_file.name, 'content': content}


def update_client_info_file(client_path: Path, section: str, content: str) -> str:
    """Append content to a section of a client INFO file. Creates backup.

    Returns the backup filename.
    Raises ValueError if no INFO file is found.
    """
    import shutil
    info_files = list(client_path.glob("*INFO*.md"))
    if not info_files:
        raise ValueError(f"No INFO file found for '{client_path.name}'.")

    info_file = sorted(info_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]

    backup = info_file.with_suffix('.md.bak')
    shutil.copy2(info_file, backup)

    existing = info_file.read_text(encoding="utf-8")
    section_header = f"## {section}"
    if section_header in existing:
        parts = existing.split(section_header, 1)
        after_header = parts[1]
        next_section_idx = after_header.find("\n## ")
        if next_section_idx == -1:
            new_content = existing + f"\n{content}\n"
        else:
            insert_point = len(parts[0]) + len(section_header) + next_section_idx
            new_content = existing[:insert_point] + f"\n{content}\n" + existing[insert_point:]
    else:
        new_content = existing.rstrip() + f"\n\n{section_header}\n{content}\n"

    info_file.write_text(new_content, encoding="utf-8")
    return backup.name


def get_template_sections(config: Config):
    template_path = PathManager.get_info_template_path()
    client_part = ""
    service_part = ""

    if not template_path.exists():
        return CLIENT_TEMPLATE_STR, SERVICE_TEMPLATE_STR

    try:
        import re
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = re.split(r'##\s*INFO-SERVICO\.md', content, flags=re.IGNORECASE)
        client_part = parts[0]
        if len(parts) > 1:
            service_part = "## INFO-SERVICO.md" + parts[1]
        else:
            service_part = SERVICE_TEMPLATE_STR

        return client_part, service_part
    except Exception as e:
        logger.error(f"Erro ao carregar template DNA: {e}")
        return CLIENT_TEMPLATE_STR, SERVICE_TEMPLATE_STR


def _generate_filename(cod, alias, ver="00", rev="R00"):
    return f"{cod}_DOC_CD_{ver}_{rev}_INFO-{alias}.md"


def _parse_filename(filename):
    try:
        parts = filename.stem.split('_')
        if len(parts) >= 6:
            return parts[3], parts[4]
    except Exception:
        pass
    return "00", "R00"


def _increment_revision(rev):
    num = int(rev[1:]) if len(rev) > 1 and rev[1:].isdigit() else 0
    return f"R{num + 1:02d}"


def _get_latest_file(folder, alias):
    if not folder.exists():
        return None
    files = list(folder.glob(f"*_INFO-{alias}.md"))
    if not files:
        return None

    def sort_key(f):
        ver, rev = _parse_filename(f)
        return (ver, rev)

    files.sort(key=sort_key, reverse=True)
    return files[0]


def _read_file_content(path):
    data = {}
    if not path.exists():
        return data
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if ';' in line:
                key, value = line.split(';', 1)
                data[key.strip()] = value.strip()
            elif ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
    return data


def _write_formatted_file_content(path, data, template_str):
    import re
    lines = template_str.split('\n')
    output_lines = []
    written_keys = set()

    for line in lines:
        stripped = line.strip()
        sep = ';' if ';' in stripped else (':' if ':' in stripped else None)

        if stripped.startswith('@') and sep:
            key = stripped.split(sep)[0].strip()
            written_keys.add(key)
            value = data.get(key, "")
            output_lines.append(f"{key}; {value}")
        else:
            output_lines.append(line)

    extra_keys = [k for k in data.keys() if k not in written_keys and k.startswith('@')]
    if extra_keys:
        output_lines.append("\n### VARIÁVEIS EXTRAS")
        for key in extra_keys:
            output_lines.append(f"{key}; {data[key]}")

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))


def _generate_service_code(client_alias, service_alias):
    base = (client_alias[:3] + service_alias[:3]).upper()
    base = ''.join(filter(str.isalnum, base))
    return f"{base}01"


def create_client(name: str, repository, config: Config, tax_id: str = "",
                  email: str = "", phone: str = "", alias: str = ""):
    if not validate_filename(name):
        raise ValueError("Nome do cliente contém caracteres inválidos ou é reservado.")
    if alias and not validate_filename(alias):
        raise ValueError("Alias do cliente contém caracteres inválidos ou é reservado.")

    db_clients = repository.get_clients_dataframe()

    existing_codes = set(db_clients['CodCliente'].dropna().values) if 'CodCliente' in db_clients else set()
    codigo = generate_client_code(name, existing_codes)

    dados = {
        "CodCliente": codigo,
        "NomeCliente": name,
        "NIF": tax_id,
        "Email": email,
        "Telefone": phone,
        "Alias": alias or name,
    }

    new_row = pd.DataFrame([dados])
    updated_df = pd.concat([db_clients, new_row], ignore_index=True)
    updated_df = format_columns(updated_df)
    repository.save_clients(updated_df)

    caminho = config.base_pasta_clientes / name
    caminho.mkdir(parents=True, exist_ok=True)

    logger.info(f"Cliente {name} ({codigo}) criado com sucesso em {caminho}.")

    # Keep the CreatedClient dataclass importable from outside
    from foton_system.modules.clients.application.use_cases.client_service import CreatedClient
    return CreatedClient(codigo=codigo, caminho=caminho, dados=dados)


def export_client_data(repository, config: Config):
    logger.info("Exporting client data to files...")
    count = 0
    try:
        client_template, _ = get_template_sections(config)
        df = repository.get_clients_dataframe()
        latest_df = df.groupby('Alias').last().reset_index()

        for _, row in latest_df.iterrows():
            alias = row['Alias']
            cod = row.get('CodCliente')
            if not cod:
                cod = generate_client_code(row.get('NomeCliente', ''), set())

            folder = config.base_pasta_clientes / alias
            if not folder.exists():
                continue

            file_data = row.dropna().to_dict()
            latest_file = _get_latest_file(folder, alias)

            should_create = False
            ver, rev = "00", "R00"
            existing_data = {}

            if latest_file:
                existing_data = _read_file_content(latest_file)
                merged_data = {**existing_data, **file_data}

                is_different = any(str(v) != existing_data.get(k) for k, v in merged_data.items())

                if is_different:
                    should_create = True
                    ver, rev = _parse_filename(latest_file)
                    rev = _increment_revision(rev)

                file_data = merged_data
            else:
                should_create = True

            if should_create:
                filename = _generate_filename(cod, alias, ver, rev)
                _write_formatted_file_content(folder / filename, file_data, client_template)
                count += 1

        logger.info(f"{count} arquivos de cliente exportados/atualizados.")
    except Exception as e:
        logger.error(f"Erro ao exportar dados de clientes: {e}")


def export_service_data(repository, config: Config):
    logger.info("Exporting service data to files...")
    count = 0
    try:
        _, service_template = get_template_sections(config)
        df = repository.get_services_dataframe()
        latest_df = df.groupby(['AliasCliente', 'Alias']).last().reset_index()

        for _, row in latest_df.iterrows():
            client_alias = row['AliasCliente']
            service_alias = row['Alias']

            cod = row.get('CodServico')
            if not cod or pd.isna(cod):
                cod = _generate_service_code(client_alias, service_alias)

            folder = config.base_pasta_clientes / client_alias / service_alias
            if not folder.exists():
                continue

            file_data = row.dropna().to_dict()
            file_data['CodServico'] = cod

            latest_file = _get_latest_file(folder, service_alias)

            should_create = False
            ver, rev = "00", "R00"
            existing_data = {}

            if latest_file:
                existing_data = _read_file_content(latest_file)
                merged_data = {**existing_data, **file_data}

                is_different = any(str(v) != existing_data.get(k) for k, v in merged_data.items())

                if is_different:
                    should_create = True
                    ver, rev = _parse_filename(latest_file)
                    rev = _increment_revision(rev)

                file_data = merged_data
            else:
                should_create = True

            if should_create:
                filename = _generate_filename(cod, service_alias, ver, rev)
                _write_formatted_file_content(folder / filename, file_data, service_template)
                count += 1

        logger.info(f"{count} arquivos de serviço exportados/atualizados.")
    except Exception as e:
        logger.error(f"Erro ao exportar dados de serviços: {e}")


def import_service_data(repository, config: Config):
    import pandas as pd
    logger.info("Importing service data from files...")
    count = 0
    try:
        df = repository.get_services_dataframe()
        folder_clients = repository.list_client_folders()

        new_rows = []

        for client_alias in folder_clients:
            service_folders = repository.list_service_folders(client_alias)
            for service_alias in service_folders:
                folder = config.base_pasta_clientes / client_alias / service_alias
                latest_file = _get_latest_file(folder, service_alias)

                if not latest_file:
                    continue

                file_data = _read_file_content(latest_file)
                if not file_data:
                    continue

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
                file_data['AliasCliente'] = client_alias
                file_data['Alias'] = service_alias

                new_rows.append(file_data)
                count += 1

        if new_rows:
            new_df = pd.DataFrame(new_rows)
            updated_df = pd.concat([df, new_df], ignore_index=True)
            repository.save_services(updated_df)
            logger.info(f"{count} registros de serviço importados/atualizados.")
        else:
            logger.info("Nenhuma alteração encontrada nos arquivos de serviço.")

    except Exception as e:
        logger.error(f"Erro ao importar dados de serviços: {e}")


def sync_clients_db_from_folders(repository):
    logger.info("Sincronizando base de clientes a partir das pastas...")
    try:
        db_clients = repository.get_clients_dataframe()
        existing_aliases = set(db_clients['Alias'].dropna().unique())
        folder_aliases = repository.list_client_folders()

        new_aliases = folder_aliases - existing_aliases

        if not new_aliases:
            logger.info("Nenhum cliente novo encontrado nas pastas.")
            return

        new_data = pd.DataFrame({'Alias': list(new_aliases)})
        updated_df = pd.concat([db_clients, new_data], ignore_index=True)
        repository.save_clients(updated_df)
        logger.info(f"{len(new_aliases)} novos clientes adicionados à base.")

    except Exception as e:
        logger.error(f"Erro na sincronização de clientes (DB <- Pastas): {e}")


def sync_client_folders_from_db(repository, config: Config):
    logger.info("Sincronizando pastas de clientes a partir da base...")
    try:
        db_clients = repository.get_clients_dataframe()
        existing_aliases = set(db_clients['Alias'].dropna().unique())
        folder_aliases = repository.list_client_folders()

        missing_folders = existing_aliases - folder_aliases

        if not missing_folders:
            logger.info("Todas as pastas de clientes já existem.")
            return

        for alias in missing_folders:
            repository.create_folder(config.base_pasta_clientes / alias)

        logger.info(f"{len(missing_folders)} pastas de clientes criadas.")

    except Exception as e:
        logger.error(f"Erro na sincronização de clientes (Pastas <- DB): {e}")


def sync_services_db_from_folders(repository, config: Config):
    logger.info("Sincronizando base de serviços a partir das pastas...")
    try:
        db_services = repository.get_services_dataframe()
        registered_services = db_services.groupby('AliasCliente')['Alias'].apply(set).to_dict()

        folder_clients = repository.list_client_folders()
        new_services_list = []
        ignored = set(config.ignored_folders)

        for client in folder_clients:
            client_services = repository.list_service_folders(client)
            known_services = registered_services.get(client, set())
            actual_services = {s for s in client_services if s not in ignored}
            missing_in_db = actual_services - known_services

            for service in missing_in_db:
                new_services_list.append({'AliasCliente': client, 'Alias': service})

        if not new_services_list:
            logger.info("Nenhum serviço novo encontrado nas pastas.")
            return

        new_df = pd.DataFrame(new_services_list)
        updated_df = pd.concat([db_services, new_df], ignore_index=True)
        repository.save_services(updated_df)
        logger.info(f"{len(new_services_list)} novos serviços adicionados à base.")

    except Exception as e:
        logger.error(f"Erro na sincronização de serviços (DB <- Pastas): {e}")


def sync_service_folders_from_db(repository, config: Config, client_alias=None):
    logger.info(f"Sincronizando pastas de serviços a partir da base... {'(Cliente: ' + client_alias + ')' if client_alias else '(Todos)'}")
    try:
        db_services = repository.get_services_dataframe()
        if client_alias:
            db_services = db_services[db_services['AliasCliente'] == client_alias]

        folder_clients = repository.list_client_folders()

        count = 0
        for index, row in db_services.iterrows():
            client = row['AliasCliente']
            service = row['Alias']

            if pd.isna(client) or pd.isna(service):
                continue
            if client not in folder_clients:
                continue

            service_path = config.base_pasta_clientes / client / service
            if not service_path.exists():
                repository.create_folder(service_path)
                count += 1

        if count == 0:
            logger.info("Todas as pastas de serviços já existem.")
        else:
            logger.info(f"{count} pastas de serviços criadas.")

    except Exception as e:
        logger.error(f"Erro na sincronização de serviços (Pastas <- DB): {e}")
