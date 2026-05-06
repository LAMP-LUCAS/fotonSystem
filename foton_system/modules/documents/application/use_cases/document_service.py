import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.documents.application.ports.document_service_port import DocumentServicePort
from foton_system.modules.shared.infrastructure.utils.formatting import FotonFormatter
from foton_system.modules.shared.infrastructure.services.cub_service import CubService
from foton_system.modules.shared.domain.exceptions import (
    TemplateNotFoundError,
    DocumentGenerationError
)

logger = setup_logger()


class DocumentService:
    def __init__(self, docx_adapter: DocumentServicePort, pptx_adapter: DocumentServicePort, config: Optional[Config] = None):
        """
        Initialize DocumentService with adapters and optional config.
        
        Args:
            docx_adapter: Adapter for DOCX document handling
            pptx_adapter: Adapter for PPTX document handling
            config: Configuration object. If None, uses default Config singleton.
        """
        self.docx_handler = docx_adapter
        self.pptx_handler = pptx_adapter
        self._config = config or Config()

    def list_templates(self, extension):
        templates_dir = self._config.templates_path
        if not templates_dir.exists():
            logger.warning(f"Diretório de templates não encontrado: {templates_dir}")
            return []
        
        return [f.name for f in templates_dir.glob(f'*.{extension}')]

    def list_data_files(self):
        data_dir = self._config.templates_path
        if not data_dir.exists():
            return []

        files = list(data_dir.glob('*.txt')) + list(data_dir.glob('*.json'))
        return [f.name for f in files]

    def list_client_data_files(self, client_path):
        client_path = Path(client_path)
        if not client_path.exists():
            return []
        return list(client_path.glob('*.md')) + list(client_path.glob('*.txt'))

    def create_custom_data_file(self, client_path, cod, ver='00', rev='R00', desc='PROPOSTA'):
        client_path = Path(client_path)
        if not client_path.exists():
            return None

        filename = f"02-{cod}_DOC_PC_{ver}_{rev}_{desc}.md"
        data_file = client_path / filename

        if data_file.exists():
            logger.warning(f"Arquivo já existe: {filename}")
            return data_file

        content = """@TEMPLATE: nome do arquivo template a ser utilizado
# DADOS ESPECÍFICOS DO DOCUMENTO
@DataAtual:
@numeroProposta:
@detalhesProposta:
@valorProposta:
"""
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Arquivo de dados criado em: {data_file}")
            return data_file
        except Exception as e:
            logger.error(f"Erro ao criar arquivo de dados: {e}")
            return None

    def generate_document(self, template_path, data_path, output_path, doc_type):
        logger.info(f"Gerando documento do tipo {doc_type}...")

        # 1. Load Context Data (Centers of Truth)
        context_data = self._load_context_data(Path(data_path))

        # 2. Load Document Data
        doc_data = self._load_data(data_path)
        
        # 3. Inject System Variables (Auto-Context)
        system_vars = self._get_system_variables()
        
        if not doc_data and not context_data:
            logger.error("Nenhum dado carregado (nem do arquivo nem do contexto).")
            # We proceed anyway because we might rely on system variables or manual fixes
        
        # 4. Merge (System < Context < Document)
        replacements = {**system_vars, **context_data, **doc_data}

        # 5. Resolve Operations (Calculated Fields)
        self._resolve_operations(replacements)

        # 6. Apply Formatting (Auto-Formatting Middleware)
        self._apply_formatting(replacements)

        # Validate Keys
        missing_keys = self._validate_keys(template_path, replacements, doc_type)

        # Clean missing variables
        if missing_keys and self._config.clean_missing_variables:
            placeholder = self._config.missing_variable_placeholder
            logger.info(f"Limpando {len(missing_keys)} variáveis faltando com placeholder '{placeholder}'")
            for key in missing_keys:
                replacements[key] = placeholder

        if doc_type == 'pptx':
            presentation = self.pptx_handler.load_document(template_path)
            presentation = self.pptx_handler.replace_text(presentation, replacements)
            self.pptx_handler.save_document(presentation, output_path)

        elif doc_type == 'docx':
            document = self.docx_handler.load_document(template_path)
            document = self.docx_handler.replace_text(document, replacements)
            self.docx_handler.save_document(document, output_path)

        else:
            logger.error(f"Tipo de documento desconhecido: {doc_type}")
            return

        # Log generation
        self._log_generation(output_path, doc_type, template_path, data_path)

    def _get_system_variables(self):
        """Injects dynamic system variables"""
        return {
            '@DataAtual': FotonFormatter.get_full_date(),
            '@LinkCUB': CubService.get_dynamic_url(),
            '@ReferenciaCUB': CubService.get_reference_label()
        }

    def _apply_formatting(self, replacements):
        """
        Iterates over all keys and applies smart formatting rules.
        PURE DATA POLICY: No automatic 'R$' prefix or 'm²' suffix.
        """
        for key, value in replacements.items():
            # Apply smart formatting: literals in quotes remain raw, numbers get BR decimal format, % get percentage format
            replacements[key] = FotonFormatter.smart_format(key, value)

    def _load_context_data(self, data_path):
        data = {}
        try:
            base_clients = self._config.base_pasta_clientes
            current_dir = data_path.parent

            dirs_to_check = []
            while current_dir != base_clients and current_dir != current_dir.parent:
                dirs_to_check.append(current_dir)
                current_dir = current_dir.parent

            dirs_to_check.reverse()

            for folder in dirs_to_check:
                # Find any *INFO*.md file in the folder, regardless of folder name
                info_files = list(folder.glob("*INFO*.md"))
                if info_files:
                    # Sort by modification time to get the most recent if multiple exist
                    info_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                    info_file = info_files[0]
                    logger.info(f"Carregando contexto de: {info_file.name} em {folder.name}")
                    folder_data = self._parse_md_data(info_file)
                    # Lowercase keys for case-insensitive matching
                    normalized_folder_data = {k.lower(): v for k, v in folder_data.items()}
                    data.update(normalized_folder_data)

        except Exception as e:
            logger.warning(f"Erro ao carregar dados de contexto: {e}")

        return data

    def _parse_md_data(self, file_path):
        """
        Parses metadata from an MD file.
        Format: @Variable; Value
        """
        data = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('@'):
                        if ';' in line:
                            parts = line.split(';', 1)
                            key = parts[0].strip()
                            value = parts[1].strip()
                            data[key] = value
                        elif ':' in line: # Fallback for older files
                            parts = line.split(':', 1)
                            key = parts[0].strip()
                            value = parts[1].strip()
                            data[key] = value
        except Exception as e:
            logger.error(f"Erro ao parsear {file_path}: {e}")
        return data

    def _load_data(self, data_path):
        """
        Loads data from the specific file (usually the one being used for generation).
        """
        if not data_path.exists():
            return {}
        
        raw_data = self._parse_md_data(data_path)
        # Lowercase keys for case-insensitive matching
        return {k.lower(): v for k, v in raw_data.items()}

    def _get_latest_info_file(self, folder, alias):
        # This method is now deprecated by the new glob logic in _load_context_data
        # but kept for potential backward compatibility if called elsewhere.
        files = list(folder.glob("*INFO*.md"))
        if not files:
            return None

        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return files[0]

    def validate_template_keys(self, template_path, data_path, doc_type):
        """
        Public method to validate template keys against context and local data.
        Ensures everything is case-insensitive by lowercasing keys.
        """
        context_data = self._load_context_data(Path(data_path))
        doc_data = self._load_data(Path(data_path))
        replacements = {**context_data, **doc_data}
        return self._validate_keys(template_path, replacements, doc_type)

    def _validate_keys(self, template_path, replacements, doc_type):
        required_keys = set()
        try:
            if doc_type == 'docx':
                doc = self.docx_handler.load_document(template_path)
                for p in doc.paragraphs:
                    self._extract_keys_from_text(p.text, required_keys)
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for p in cell.paragraphs:
                                self._extract_keys_from_text(p.text, required_keys)
                for section in doc.sections:
                    for p in section.header.paragraphs:
                        self._extract_keys_from_text(p.text, required_keys)
                    for p in section.footer.paragraphs:
                        self._extract_keys_from_text(p.text, required_keys)

            elif doc_type == 'pptx':
                prs = self.pptx_handler.load_document(template_path)
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if shape.has_text_frame:
                            for p in shape.text_frame.paragraphs:
                                self._extract_keys_from_text(p.text, required_keys)
                        if shape.has_table:
                             for row in shape.table.rows:
                                for cell in row.cells:
                                    if cell.text_frame:
                                        for p in cell.text_frame.paragraphs:
                                            self._extract_keys_from_text(p.text, required_keys)
        except Exception as e:
            logger.warning(f"Não foi possível validar as chaves do template: {e}")
            return []

        # All keys are normalized to lowercase for comparison
        missing_keys = [k for k in required_keys if k.lower() not in replacements]
        if missing_keys:
            logger.warning(f"CHAVES FALTANDO: {missing_keys}")

        return missing_keys

    def _log_generation(self, output_path, doc_type, template_path, data_path):
        try:
            client_dir = Path(output_path).parent
            history_file = client_dir / 'history.log'
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            template_name = Path(template_path).name
            data_name = Path(data_path).name
            output_name = Path(output_path).name
            log_entry = f"[{timestamp}] Documento '{output_name}' ({doc_type}) gerado usando Template '{template_name}' e Dados '{data_name}'\n"
            with open(history_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            logger.error(f"Erro ao gravar log de geração: {e}")

    def _extract_keys_from_text(self, text, keys_set):
        """Extracts keys from text and normalizes them to lowercase for consistent validation."""
        if text and '@' in text:
            found = re.findall(r'(?<![\w.])@[\w%]+(?!\.[a-z]{2,}\b)', text)
            for k in found:
                keys_set.add(k.lower())

    def _resolve_operations(self, replacements):
        """
        Resolves mathematical operations.
        Improvement: Handles Brazilian number formats during calculation.
        """
        for _ in range(3):
            # Normalize keys for lookup
            current_keys = list(replacements.keys())
            for key in current_keys:
                value = replacements[key]
                if isinstance(value, str) and '[calculo:' in value:
                    match = re.search(r'\[calculo:\s*(.+?)\]', value)
                    if match:
                        expression = match.group(1)
                        # Sort keys by length to avoid partial matches during calculation replacement
                        for k in sorted(current_keys, key=len, reverse=True):
                            v = replacements[k]
                            if k.lower() in expression.lower() and k != key:
                                try:
                                    # Normalize to float for calculation
                                    float_val = FotonFormatter.parse_br_number(v)
                                    # Case-insensitive replacement of variable in expression
                                    expression = re.sub(re.escape(k), str(float_val), expression, flags=re.IGNORECASE)
                                except:
                                    pass
                        try:
                            if not re.match(r'^[\d\.\-\+\*\/\(\)\s]+$', expression):
                                raise ValueError("Expressão contém caracteres inválidos")

                            result = eval(expression)
                            replacements[key] = str(result)
                        except Exception as e:
                            logger.warning(f"Falha ao calcular {key}: {e}")
