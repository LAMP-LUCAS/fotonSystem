import pandas as pd
from pathlib import Path
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.documents.application.use_cases.document_service import DocumentService

logger = setup_logger()

class SyncService:
    def sync_dashboard(self):
        """
        Lê todas as pastas de clientes e atualiza o baseDados.xlsx
        """
        base_path = Config().base_pasta_clientes
        db_path = Config().base_dados
        
        logger.info(f"Iniciando sincronização de {base_path} para {db_path}...")
        
        # Reutiliza lógica de parsing do DocumentService
        doc_service = DocumentService(None, None)
        
        records = []

        # Varre diretórios (Assumindo profundidade 1 ou 2)
        # Ajuste conforme estrutura real: CLIENTES/NOME/INFO.md
        for client_dir in base_path.iterdir():
            if client_dir.is_dir():
                info_file = list(client_dir.glob("INFO-CLIENTE.md"))
                if info_file:
                    data = doc_service._parse_md_data(info_file[0])
                    # Adiciona metadados de sistema
                    data['Origem'] = str(client_dir)
                    data['UltimaAtualizacao'] = pd.Timestamp.now()
                    records.append(data)
        
        if not records:
            logger.warning("Nenhum cliente encontrado para sincronizar.")
            return

        df = pd.DataFrame(records)
        
        # Normaliza colunas (remove @)
        df.columns = [c.replace('@', '') for c in df.columns]
        
        try:
            # Salva/Atualiza Excel
            if db_path.exists():
                # Poderíamos fazer merge inteligente, mas overwrite é mais seguro para "Fonte de Verdade"
                pass
            
            df.to_excel(db_path, index=False)
            logger.info(f"Dashboard atualizado com sucesso: {len(records)} registros.")
            return df
        except Exception as e:
            logger.error(f"Erro ao salvar Dashboard: {e}")
