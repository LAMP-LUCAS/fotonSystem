import unicodedata
import re
from typing import Optional


def normalize_client_name(name: Optional[str]) -> str:
    if not name:
        return ""
    normalized = unicodedata.normalize('NFKD', name)
    normalized = normalized.encode('ascii', 'ignore').decode('ascii')
    normalized = normalized.upper()
    normalized = re.sub(r'[-\s]+', '_', normalized)
    normalized = re.sub(r'[^A-Z0-9_]', '', normalized)
    normalized = re.sub(r'_+', '_', normalized)
    normalized = normalized.strip('_')
    return normalized


def format_date(date_val):
    import pandas as pd
    try:
        return pd.to_datetime(date_val, format='%d-%m-%Y').strftime('%Y-%m-%d')
    except Exception:
        return date_val


def format_cpf_cnpj(val):
    return ''.join(re.findall(r'\d+', str(val)))


def format_columns(df):
    import pandas as pd
    for idx, row in df.iterrows():
        if 'DataServico' in row and pd.notna(row['DataServico']):
            df.at[idx, 'DataServico'] = format_date(row['DataServico'])
        if 'CPF' in row and pd.notna(row['CPF']):
            df.at[idx, 'CPF'] = format_cpf_cnpj(row['CPF'])
        if 'CNPJ' in row and pd.notna(row['CNPJ']):
            df.at[idx, 'CNPJ'] = format_cpf_cnpj(row['CNPJ'])
    return df
