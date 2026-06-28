from pathlib import Path
from typing import Optional

import pandas as pd

from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.shared.infrastructure.validators import validate_filename
from foton_system.modules.shared.domain.exceptions import InvalidAliasError, DatabaseLockError, ValidationError
from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name, format_columns
from foton_system.modules.clients.application.use_cases.client_query import resolve_client_path, generate_client_code, list_service_nodes
from foton_system.modules.clients.domain.models import Client
from foton_system.modules.clients.domain.value_objects import ClientCode, TaxId

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


def update_client_info_file(client_path: Path, section: str, content: str,
                            operacao: str = "append", campo: str = "") -> str:
    """Update a client INFO file with various operations. Creates backup.

    Operations:
      - "append" (default): append content to a section
      - "replace": replace entire section content
      - "remove": remove section entirely
      - "field": update @campo value via regex

    Returns the backup filename.
    Raises ValueError if no INFO file or target not found.
    """
    import re
    import shutil
    info_files = list(client_path.glob("*INFO*.md"))
    if not info_files:
        raise ValueError(f"No INFO file found for '{client_path.name}'.")

    info_file = sorted(info_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]

    backup = info_file.with_suffix('.md.bak')
    shutil.copy2(info_file, backup)

    existing = info_file.read_text(encoding="utf-8")
    section_header = f"## {section}"

    if operacao == "remove":
        if section_header not in existing:
            raise ValueError(f"Section '{section}' not found in INFO file.")
        before, after = existing.split(section_header, 1)
        after_stripped = after.lstrip('\n')
        next_section_idx = after_stripped.find("\n## ")
        if next_section_idx == -1:
            new_content = before.rstrip() + "\n"
        else:
            new_content = before + after_stripped[next_section_idx:]

    elif operacao == "replace":
        if section_header not in existing:
            raise ValueError(f"Section '{section}' not found in INFO file.")
        before, after = existing.split(section_header, 1)
        after_stripped = after.lstrip('\n')
        next_section_idx = after_stripped.find("\n## ")
        if next_section_idx == -1:
            new_content = before + section_header + "\n" + content + "\n"
        else:
            new_content = (before + section_header + "\n" + content + "\n"
                           + after_stripped[next_section_idx:])

    elif operacao == "field":
        if not campo:
            raise ValueError("Field name (campo) is required for 'field' operation.")
        pattern = rf'(@{re.escape(campo)})\s*[:;]\s*[^\n]*'
        if not re.search(pattern, existing):
            raise ValueError(f"Field '@{campo}' not found in INFO file.")
        new_content = re.sub(pattern, rf'\1: {content}', existing)

    else:
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
    from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
    info_template_path = PathManager.get_info_template_path()
    client_header = PathManager.get_info_header("cliente")
    service_header = PathManager.get_info_header("servico")
    client_part = ""
    service_part = ""

    # Helper: substitui headers hardcoded no template pelos do pattern
    def _replace_headers(text: str) -> str:
        return (text
                .replace("## INFO-CLIENTE.md", client_header)
                .replace("## INFO-SERVICO.md", service_header)
                .replace("## INFO-CLIENTE", client_header)
                .replace("## INFO-SERVICO", service_header))

    if not info_template_path.exists():
        return _replace_headers(CLIENT_TEMPLATE_STR), _replace_headers(SERVICE_TEMPLATE_STR)

    try:
        import re
        with open(info_template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Divide nas seções INFO-SERVICO (header original ou do pattern)
        pattern_header_escaped = re.escape(service_header)
        parts = re.split(pattern_header_escaped, content, flags=re.IGNORECASE)
        client_part = parts[0]
        if len(parts) > 1:
            service_part = service_header + parts[1]
        else:
            # Fallback: tenta dividir pelo header original
            parts = re.split(r'##\s*INFO-SERVICO[\.\w]*', content, flags=re.IGNORECASE)
            client_part = parts[0]
            if len(parts) > 1:
                service_part = service_header + parts[1]
            else:
                service_part = _replace_headers(SERVICE_TEMPLATE_STR)

        return _replace_headers(client_part), _replace_headers(service_part)
    except Exception as e:
        logger.error(f"Erro ao carregar template DNA: {e}")
        return _replace_headers(CLIENT_TEMPLATE_STR), _replace_headers(SERVICE_TEMPLATE_STR)


def _resolve_info_filename(tipo: str, **placeholders) -> str:
    """Gera nome de arquivo INFO usando o pattern configurável."""
    from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
    resolver = PathManager.get_info_pattern(tipo)
    return resolver.resolve(**placeholders)


def _parse_revision_from_filename(filename, tipo: str):
    """Extrai versão e revisão do filename usando extract() do pattern."""
    from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
    resolver = PathManager.get_info_pattern(tipo)
    extracted = resolver.extract(filename.name if hasattr(filename, 'name') else str(filename))
    ver = extracted.get('versao', '00')
    rev = extracted.get('revisao', '')
    return ver, f"R{rev}" if rev else "R00"


def _increment_revision(rev):
    num = int(rev[1:]) if len(rev) > 1 and rev[1:].isdigit() else 0
    return f"R{num + 1:02d}"


def _get_latest_file(folder, tipo: str):
    """Busca o arquivo INFO mais recente usando o glob do pattern."""
    if not folder.exists():
        return None
    from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
    glob_pattern = PathManager.get_info_glob(tipo)
    files = list(folder.glob(glob_pattern))
    if not files:
        return None

    def sort_key(f):
        ver, rev = _parse_revision_from_filename(f, tipo)
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


def generate_service_code(client_alias, service_alias, existing_codes=None):
    """Gera código único para serviço. Se existing_codes for fornecido, evita colisões."""
    base = (client_alias[:3] + service_alias[:3]).upper()
    base = ''.join(filter(str.isalnum, base))
    code = f"{base}01"
    if existing_codes is not None:
        counter = 1
        while code in existing_codes:
            counter += 1
            code = f"{base}{counter:02d}"
    return code


def _generate_service_code(client_alias, service_alias):
    return generate_service_code(client_alias, service_alias)


def fill_missing_codes(repository, config=None) -> dict:
    """Preenche CodCliente e CodServico faltantes (NaN) no banco de dados.

    Returns:
        dict com contadores: clientes_alterados, servicos_alterados
    """
    result = {"clientes_alterados": 0, "servicos_alterados": 0}

    # Preenche CodCliente
    df = repository.get_clients_dataframe()
    existing_codes = set(df['CodCliente'].dropna().values) if 'CodCliente' in df else set()
    changed = False
    for idx, row in df.iterrows():
        cod = row.get('CodCliente')
        if not cod or (isinstance(cod, float) and pd.isna(cod)):
            name = row.get('NomeCliente')
            if isinstance(name, float) and pd.isna(name):
                name = ''
            cod = generate_client_code(name, existing_codes)
            df.at[idx, 'CodCliente'] = str(cod) if cod is not None else cod
            existing_codes.add(cod)
            result["clientes_alterados"] += 1
            changed = True
    if changed:
        df['CodCliente'] = df['CodCliente'].astype(object)
        repository.save_clients(df)

    # Preenche CodServico
    sdf = repository.get_services_dataframe()
    existing_service_codes = set(sdf['CodServico'].dropna().values) if 'CodServico' in sdf else set()
    changed_svc = False
    for idx, row in sdf.iterrows():
        cod = row.get('CodServico')
        if not cod or (isinstance(cod, float) and pd.isna(cod)):
            client_alias = row.get('AliasCliente')
            if isinstance(client_alias, float) and pd.isna(client_alias):
                client_alias = ''
            service_alias = row.get('Alias')
            if isinstance(service_alias, float) and pd.isna(service_alias):
                service_alias = ''
            cod = generate_service_code(client_alias, service_alias, existing_service_codes)
            sdf.at[idx, 'CodServico'] = str(cod) if cod is not None else cod
            existing_service_codes.add(cod)
            result["servicos_alterados"] += 1
            changed_svc = True
    if changed_svc:
        sdf['CodServico'] = sdf['CodServico'].astype(object)
        repository.save_services(sdf)

    logger.info(f"Códigos preenchidos: {result['clientes_alterados']} clientes, {result['servicos_alterados']} serviços.")
    return result


def create_client(name: str, repository, config: Config, tax_id: str = "",
                  email: str = "", phone: str = "", alias: str = ""):
    if not validate_filename(name):
        raise ValueError("Nome do cliente contém caracteres inválidos ou é reservado.")
    if alias and not validate_filename(alias):
        raise ValueError("Alias do cliente contém caracteres inválidos ou é reservado.")

    db_clients = repository.get_clients_dataframe()

    import re
    import unicodedata

    existing_codes = set(db_clients['CodCliente'].dropna().values) if 'CodCliente' in db_clients else set()

    codigo_raw = generate_client_code(name, existing_codes)

    # Normalize: strip accents and keep only A-Z/0-9, then ensure client code format
    codigo = None
    if codigo_raw:
        normalized = ''.join(
            c for c in unicodedata.normalize('NFKD', codigo_raw)
            if not unicodedata.combining(c)
        )
        normalized = re.sub(r'[^A-Z0-9]', '', normalized.upper())
        if re.match(r'^[A-Z]{3,5}[0-9]{2}$', normalized):
            codigo = normalized
        else:
            # Strip digits from end, use letters-only as base, then append "01"
            base = re.sub(r'[0-9]+$', '', normalized) or normalized
            base = re.sub(r'[^A-Z]', '', base) or 'XXX'
            if len(base) > 5:
                base = base[:5]
            if not re.match(r'^[A-Z]{3,5}$', base):
                base = (base + 'XX')[:5]
            codigo = base + '01'
            existing_codes.add(codigo_raw)
            while codigo in existing_codes:
                num = int(codigo[-2:]) + 1
                codigo = f"{base}{num:02d}"

    client_codigo = ClientCode(codigo) if codigo else None
    try:
        client_nif = TaxId(tax_id) if tax_id else None
    except ValueError:
        client_nif = None

    client = Client(
        nome=name,
        alias=alias or name,
        codigo=client_codigo,
        nif=client_nif,
        email=email,
        telefone=phone,
        status="ATIVO",
    )

    dados = client.to_row()

    new_row = pd.DataFrame([dados])
    updated_df = pd.concat([db_clients, new_row], ignore_index=True)
    updated_df = format_columns(updated_df)
    repository.save_clients(updated_df)

    caminho = config.base_pasta_clientes / name
    caminho.mkdir(parents=True, exist_ok=True)

    logger.info(f"Cliente {name} ({codigo}) criado com sucesso em {caminho}.")

    return client


def export_client_data(repository, config: Config, target_alias: str = None):
    """Export client data to INFO files. If target_alias set, only export that client."""
    logger.info(f"Exporting client data to files...{' (filter: ' + target_alias + ')' if target_alias else ''}")
    count = 0
    try:
        client_template, _ = get_template_sections(config)
        df = repository.get_clients_dataframe()
        latest_df = df.groupby('Alias').last().reset_index()

        df_updated = False
        for _, row in latest_df.iterrows():
            alias = row['Alias']
            if target_alias and alias != target_alias:
                continue
            cod = row.get('CodCliente')
            if not cod or (isinstance(cod, float) and pd.isna(cod)):
                existing = set(df['CodCliente'].dropna().values) if 'CodCliente' in df else set()
                cod = generate_client_code(row.get('NomeCliente', ''), existing)
                df.loc[df['Alias'] == alias, 'CodCliente'] = cod
                df_updated = True

            folder = config.base_pasta_clientes / alias
            if not folder.exists():
                continue

            file_data = row.dropna().to_dict()
            latest_file = _get_latest_file(folder, "cliente")

            should_create = False
            ver, rev = "00", "R00"
            existing_data = {}

            if latest_file:
                existing_data = _read_file_content(latest_file)
                merged_data = {**existing_data, **file_data}

                is_different = any(str(v) != existing_data.get(k) for k, v in merged_data.items())

                if is_different:
                    should_create = True
                    ver, rev = _parse_revision_from_filename(latest_file, "cliente")
                    rev = _increment_revision(rev)

                file_data = merged_data
            else:
                should_create = True

            if should_create:
                filename = _resolve_info_filename("cliente", codCliente=cod, aliasCliente=alias, versao=ver, revisao=rev)
                _write_formatted_file_content(folder / filename, file_data, client_template)
                count += 1

        if df_updated:
            repository.save_clients(df)
        logger.info(f"{count} arquivos de cliente exportados/atualizados.")
    except Exception as e:
        logger.error(f"Erro ao exportar dados de clientes: {e}")


def export_service_data(repository, config: Config, target_client_alias: str = None, target_service_alias: str = None):
    """Export service data to INFO files. If target* set, only export matching service."""
    client_filter = f" ({target_client_alias}/{target_service_alias})" if target_client_alias else ""
    logger.info(f"Exporting service data to files...{client_filter}")
    count = 0
    try:
        _, service_template = get_template_sections(config)
        df = repository.get_services_dataframe()
        latest_df = df.groupby(['AliasCliente', 'Alias']).last().reset_index()

        df_updated = False
        for _, row in latest_df.iterrows():
            client_alias = row['AliasCliente']
            service_alias = row['Alias']
            if target_client_alias and client_alias != target_client_alias:
                continue
            if target_service_alias and service_alias != target_service_alias:
                continue

            cod = row.get('CodServico')
            if not cod or pd.isna(cod):
                existing = set(df['CodServico'].dropna().values) if 'CodServico' in df else set()
                cod = generate_service_code(client_alias, service_alias, existing)
                df.loc[(df['AliasCliente'] == client_alias) & (df['Alias'] == service_alias), 'CodServico'] = cod
                df_updated = True

            folder = config.base_pasta_clientes / client_alias / service_alias
            if not folder.exists():
                continue

            file_data = row.dropna().to_dict()
            file_data['CodServico'] = cod

            latest_file = _get_latest_file(folder, "servico")

            should_create = False
            ver, rev = "00", "R00"
            existing_data = {}

            if latest_file:
                existing_data = _read_file_content(latest_file)
                merged_data = {**existing_data, **file_data}

                is_different = any(str(v) != existing_data.get(k) for k, v in merged_data.items())

                if is_different:
                    should_create = True
                    ver, rev = _parse_revision_from_filename(latest_file, "servico")
                    rev = _increment_revision(rev)

                file_data = merged_data
            else:
                should_create = True

            if should_create:
                filename = _resolve_info_filename("servico", codServico=cod, aliasServico=service_alias, versao=ver, revisao=rev)
                _write_formatted_file_content(folder / filename, file_data, service_template)
                count += 1

        if df_updated:
            repository.save_services(df)
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
                latest_file = _get_latest_file(folder, "servico")

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


def import_client_data(repository, config: Config):
    import pandas as pd
    logger.info("Importing client data from files...")
    count = 0
    try:
        df = repository.get_clients_dataframe()
        folder_aliases = repository.list_client_folders()

        new_rows = []

        for client_alias in folder_aliases:
            folder = config.base_pasta_clientes / client_alias
            latest_file = _get_latest_file(folder, "cliente")

            if not latest_file:
                continue

            file_data = _read_file_content(latest_file)
            if not file_data:
                continue

            db_entry = df[df['Alias'] == client_alias]
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
            file_data['Alias'] = client_alias
            # Garante que NomeCliente seja preenchido se ausente
            if 'NomeCliente' not in file_data or not file_data['NomeCliente']:
                file_data['NomeCliente'] = client_alias

            new_rows.append(file_data)
            count += 1

        if new_rows:
            new_df = pd.DataFrame(new_rows)
            updated_df = pd.concat([df, new_df], ignore_index=True)
            repository.save_clients(updated_df)
            logger.info(f"{count} registros de cliente importados/atualizados.")
        else:
            logger.info("Nenhuma alteração encontrada nos arquivos de cliente.")

    except Exception as e:
        logger.error(f"Erro ao importar dados de clientes: {e}")


def create_service_entry(repository, config: Config, client_alias: str, service_alias: str, cod_servico: str = None) -> dict:
    """Cria um registro de serviço no banco de dados com código único.

    Se cod_servico não for fornecido, gera automaticamente via generate_service_code().
    Verifica duplicata de alias antes de inserir.

    Returns:
        dict com 'AliasCliente', 'Alias', 'CodServico'
    Raises:
        ValueError se o par (client_alias, service_alias) já existir no DB
    """
    if not client_alias or not service_alias:
        raise ValueError("client_alias e service_alias são obrigatórios.")

    sdf = repository.get_services_dataframe()

    exists = not sdf[(sdf['AliasCliente'] == client_alias) & (sdf['Alias'] == service_alias)].empty
    if exists:
        raise ValueError(f"Serviço '{service_alias}' já existe para o cliente '{client_alias}'.")

    existing_codes = set(sdf['CodServico'].dropna().values) if 'CodServico' in sdf else set()
    if not cod_servico:
        cod_servico = generate_service_code(client_alias, service_alias, existing_codes)

    new_row = pd.DataFrame([{
        'AliasCliente': client_alias,
        'Alias': service_alias,
        'CodServico': cod_servico,
    }])
    updated_df = pd.concat([sdf, new_row], ignore_index=True)
    repository.save_services(updated_df)

    logger.info(f"Serviço '{service_alias}' ({cod_servico}) criado para '{client_alias}'.")
    return {'AliasCliente': client_alias, 'Alias': service_alias, 'CodServico': cod_servico}


def validate_service_codes(repository, config=None) -> list[dict]:
    """Valida todos os CodServico no banco de dados.

    Verifica:
    - Ausente (NaN/None)
    - Placeholder (códigos como '000' ou que não seguem o padrão alfanumérico)
    - Formato inválido (caracteres especiais, muito curto)
    - Duplicatas (mesmo código em mais de um serviço)

    Returns:
        list[dict] com: cod_servico, client_alias, service_alias, issue, suggested_fix
    """
    sdf = repository.get_services_dataframe()
    issues = []

    if 'CodServico' not in sdf:
        return issues

    code_counts = sdf['CodServico'].value_counts()

    for idx, row in sdf.iterrows():
        cod = row.get('CodServico')
        client_alias = row.get('AliasCliente', '')
        service_alias = row.get('Alias', '')

        # Missing code
        if not cod or (isinstance(cod, float) and pd.isna(cod)):
            issues.append({
                'cod_servico': '',
                'client_alias': str(client_alias) if not pd.isna(client_alias) else '',
                'service_alias': str(service_alias) if not pd.isna(service_alias) else '',
                'issue': 'missing',
                'suggested_fix': 'Preencher via preencher_codigos_faltantes()',
            })
            continue

        cod_str = str(cod)

        # Placeholder code (all zeros)
        import re
        if re.match(r'^0+$', cod_str):
            issues.append({
                'cod_servico': cod_str,
                'client_alias': str(client_alias) if not pd.isna(client_alias) else '',
                'service_alias': str(service_alias) if not pd.isna(service_alias) else '',
                'issue': 'placeholder',
                'suggested_fix': f'Gerar código único via generate_service_code("{client_alias}", "{service_alias}")',
            })
            continue

        # Invalid format (non-alphanumeric or too short)
        clean = ''.join(filter(str.isalnum, cod_str))
        if clean != cod_str or len(clean) < 4:
            issues.append({
                'cod_servico': cod_str,
                'client_alias': str(client_alias) if not pd.isna(client_alias) else '',
                'service_alias': str(service_alias) if not pd.isna(service_alias) else '',
                'issue': 'invalid_format',
                'suggested_fix': f'Corrigir formato: usar apenas caracteres alfanuméricos, mínimo 4 caracteres',
            })
            continue

        # Duplicate code
        if code_counts.get(cod_str, 0) > 1:
            issues.append({
                'cod_servico': cod_str,
                'client_alias': str(client_alias) if not pd.isna(client_alias) else '',
                'service_alias': str(service_alias) if not pd.isna(service_alias) else '',
                'issue': 'duplicate',
                'suggested_fix': f'Regenerar código único para evitar conflito com outro serviço',
            })

    logger.info(f"Validação de códigos de serviço: {len(issues)} issue(s) encontrada(s).")
    return issues


def fix_service_codes(repository, issues: list[dict]) -> int:
    """Corrige códigos de serviço inválidos/ausentes com base na lista de issues.

    Para cada issue, gera um novo código via generate_service_code().
    Persiste as correções no banco.

    Returns:
        int: número de correções aplicadas
    """
    if not issues:
        return 0

    sdf = repository.get_services_dataframe()
    existing_codes = set(sdf['CodServico'].dropna().values) if 'CodServico' in sdf else set()
    fixed_count = 0

    for issue in issues:
        client_alias = issue['client_alias']
        service_alias = issue['service_alias']
        old_code = issue['cod_servico']

        if not client_alias or not service_alias:
            continue

        mask = (sdf['AliasCliente'] == client_alias) & (sdf['Alias'] == service_alias)
        if not mask.any():
            continue

        new_code = generate_service_code(client_alias, service_alias, existing_codes)
        sdf.loc[mask, 'CodServico'] = new_code
        existing_codes.add(new_code)
        if old_code and old_code in existing_codes and old_code != new_code:
            existing_codes.discard(old_code)
        fixed_count += 1

    if fixed_count:
        sdf['CodServico'] = sdf['CodServico'].astype(object)
        repository.save_services(sdf)

    logger.info(f"{fixed_count} código(s) de serviço corrigido(s).")
    return fixed_count


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


def soft_delete_client(alias: str, repository, config: Config) -> dict:
    if not alias or not isinstance(alias, str):
        return {"success": False, "error": "Alias inválido"}
    
    df = repository.get_clients_dataframe()
    if 'Alias' not in df.columns:
        return {"success": False, "error": "Coluna Alias não encontrada"}
    
    mask = df['Alias'] == alias
    if not mask.any():
        return {"success": False, "error": f"Cliente '{alias}' não encontrado"}
    
    result = repository.soft_delete_client(alias)
    if result:
        logger.info(f"Cliente '{alias}' marcado como DELETADO")
        return {"success": True, "message": f"Cliente '{alias}' removido com sucesso"}
    return {"success": False, "error": "Falha ao remover cliente"}


def restore_client(alias: str, repository, config: Config) -> dict:
    if not alias or not isinstance(alias, str):
        return {"success": False, "error": "Alias inválido"}
    
    result = repository.restore_client(alias)
    if result:
        logger.info(f"Cliente '{alias}' restaurado")
        return {"success": True, "message": f"Cliente '{alias}' restaurado com sucesso"}
    return {"success": False, "error": f"Cliente '{alias}' não está deletado ou não existe"}


def get_deleted_clients(repository) -> list:
    return repository.get_deleted_clients()


def update_service_info(client_alias: str, service_alias: str, field: str, value, repository, config: Config) -> dict:
    valid_fields = [
        'Modalidade', 'Ano', 'Demanda', 'AreaTotal', 'AreaCoberta', 
        'AreaDescoberta', 'Detalhes', 'Estilo', 'Ambientes', 
        'ValorProposta', 'ValorContrato'
    ]
    
    if field not in valid_fields:
        return {"success": False, "error": f"Campo inválido: {field}. Campos válidos: {', '.join(valid_fields)}"}
    
    df = repository.get_services_dataframe()
    if 'AliasCliente' not in df.columns or 'Alias' not in df.columns:
        return {"success": False, "error": "Estrutura da tabela inválida"}
    
    mask = (df['AliasCliente'] == client_alias) & (df['Alias'] == service_alias)
    if not mask.any():
        return {"success": False, "error": f"Serviço '{client_alias}/{service_alias}' não encontrado"}
    
    df.loc[mask, field] = value
    repository.save_services(df)
    logger.info(f"Serviço '{client_alias}/{service_alias}' atualizado: {field}={value}")
    return {"success": True, "message": f"Campo '{field}' atualizado com sucesso"}
