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
        Iterates over all keys and applies formatting rules.
        Also creates derived keys if helpful.
        """
        formatted_replacements = {}
        
        for key, value in replacements.items():
            # Apply currency formatting if it looks like money
            # Heuristic: Key contains 'valor', 'custo', 'total', 'preco' OR Value looks like a float
            is_money_key = any(x in key.lower() for x in ['valor', 'custo', 'total', 'preco', 'cub', 'exec'])
            
            # Try to interpret as number
            try:
                # If it's already a string with 'R$', try to parse it back to float first to normalize
                clean_val = FotonFormatter.parse_br_number(value)
                
                if is_money_key:
                    # Update the MAIN key with formatted currency (User Preference)
                    replacements[key] = FotonFormatter.format_currency(clean_val)
                elif isinstance(clean_val, float) and clean_val != 0.0:
                     # It's a number but not necessarily money (e.g., Area). 
                     # Let's format as decimal (1.000,00) but keep original key flexible?
                     # For safety, let's just ensure consistent decimal formatting for areas
                     if 'area' in key.lower() or 'aceqv' in key.lower():
                         replacements[key] = FotonFormatter.format_decimal(clean_val)
            except:
                pass
                
        # We modify 'replacements' in place or update it
        # The logic above updates 'replacements' directly for specific keys

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
                alias = folder.name
                info_file = self._get_latest_info_file(folder, alias)
                if info_file:
                    logger.info(f"Carregando contexto de: {info_file.name}")
                    folder_data = self._parse_md_data(info_file)
                    data.update(folder_data)

        except Exception as e:
            logger.warning(f"Erro ao carregar dados de contexto: {e}")

        return data

    def _get_latest_info_file(self, folder, alias):
        if not folder.exists():
            return None
        files = list(folder.glob(f"*_INFO-{alias}.md"))
        if not files: # Fallback to standard INFO-{alias}.md
            files = list(folder.glob(f"INFO-{alias}.md"))
            
        if not files:
            return None

        files.sort(key=lambda f: f.name, reverse=True)
        return files[0]

    def validate_template_keys(self, template_path, data_path, doc_type):
        context_data = self._load_context_data(Path(data_path))
        doc_data = self._load_data(data_path)
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

        missing_keys = [k for k in required_keys if k not in replacements]
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
        if text and '@' in text:
            found = re.findall(r'(?<![\w.])@[\w%]+(?!\.[a-z]{2,}\b)', text)
            keys_set.update(found)

    def _load_data(self, path):
        path = str(path) # Ensure string
        if not os.path.exists(path):
            logger.error(f"Arquivo de dados não encontrado: {path}")
            return {}
        if path.endswith('.json'):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif path.endswith('.txt'):
            return self._parse_txt_data(path)
        elif path.endswith('.md'):
            return self._parse_md_data(path)
        return {}

    def _parse_txt_data(self, path):
        replacements = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(';')
                if len(parts) >= 2:
                    key, value = parts[0], parts[1]
                    replacements[key] = value
        return replacements

    def _parse_md_data(self, path):
        replacements = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    key, value = line.split(':', 1)
                    replacements[key.strip()] = value.strip()
        return replacements

    def _resolve_operations(self, replacements):
        """
        Resolves mathematical operations.
        Improvement: Handles Brazilian number formats during calculation.
        """
        for _ in range(3):
            for key, value in replacements.items():
                if isinstance(value, str) and '[calculo:' in value:
                    match = re.search(r'\[calculo:\s*(.+?)\]', value)
                    if match:
                        expression = match.group(1)
                        for k, v in replacements.items():
                            if k in expression and k != key:
                                try:
                                    # Normalize to float for calculation
                                    float_val = FotonFormatter.parse_br_number(v)
                                    expression = expression.replace(k, str(float_val))
                                except:
                                    pass
                        try:
                            if not re.match(r'^[\d\.\-\+\*\/\(\)\s]+$', expression):
                                raise ValueError("Expressão contém caracteres inválidos")

                            result = eval(expression)
                            # Store result as clean float string first to allow further calcs
                            # Or format immediately?
                            # Decision: Store as formatted string because recursive calculations 
                            # inside _resolve_operations will parse it back via parse_br_number
                            
                            # However, to be safe, let's keep it simple.
                            # The Formatter in step 6 will handle the final look.
                            # But wait, if step 6 sees "5000.00", it formats.
                            # If we store "R$ 5.000,00" here, step 6 sees string.
                            
                            # Let's return a string representation of the float
                            replacements[key] = f"{result:.2f}"
                        except Exception as e:
                            logger.warning(f"Falha ao calcular {key}: {e}")
