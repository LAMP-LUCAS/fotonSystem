import pandas as pd
from pathlib import Path
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.documents.application.use_cases.document_service import DocumentService

logger = setup_logger()

class SyncService:
    def sync_dashboard(self) -> int:
        """Lê todas as pastas de clientes e atualiza o baseDados.xlsx.

        Bug #3 fix: previously this method returned either a DataFrame
        or ``None`` (the empty case). The MCP tool layer checked truthiness
        with ``if result`` which fails for DataFrames (always truthy) and
        for ``None`` (treated as "no data"). Returning ``int`` gives a
        single, predictable contract: 0 means no clients, N > 0 means N
        records synced.
        """
        base_path = Config().base_pasta_clientes
        db_path = Config().base_dados

        logger.info(f"Iniciando sincronização de {base_path} para {db_path}...")

        _parse_md = DocumentService._parse_md_data

        records = []

        for client_dir in base_path.iterdir():
            if client_dir.is_dir():
                info_file = list(client_dir.glob("INFO-CLIENTE.md"))
                if info_file:
                    data = _parse_md(info_file[0])
                    data['Origem'] = str(client_dir)
                    data['UltimaAtualizacao'] = pd.Timestamp.now()
                    records.append(data)

        if not records:
            logger.warning("Nenhum cliente encontrado para sincronizar.")
            return 0

        df = pd.DataFrame(records)
        df.columns = [c.replace('@', '') for c in df.columns]

        try:
            df.to_excel(db_path, index=False)
            logger.info(f"Dashboard atualizado com sucesso: {len(records)} registros.")
            return len(records)
        except Exception as e:
            logger.error(f"Erro ao salvar Dashboard: {e}")
            return 0
