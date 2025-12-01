import os
import re
import json
from pathlib import Path
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.documents.application.ports.document_service_port import DocumentServicePort

logger = setup_logger()

class DocumentService:
    def __init__(self, docx_adapter: DocumentServicePort, pptx_adapter: DocumentServicePort):
        self.docx_handler = docx_adapter
        self.pptx_handler = pptx_adapter

    def list_templates(self, extension):
        """
        Lists all files with the given extension in the templates directory.
        """
        templates_dir = Config().templates_path
        if not templates_dir.exists():
            logger.warning(f"Diretório de templates não encontrado: {templates_dir}")
            return []
        
        return [f.name for f in templates_dir.glob(f'*.{extension}')]

    def list_data_files(self):
        """
        Lists all .txt and .json files in the templates directory.
        """
        data_dir = Config().templates_path
        if not data_dir.exists():
            return []
        
        files = list(data_dir.glob('*.txt')) + list(data_dir.glob('*.json'))
        return [f.name for f in files]

    def list_client_data_files(self, client_path):
        """
        Lists all .md and .txt files in the client directory.
        """
        client_path = Path(client_path)
        if not client_path.exists():
            return []
        # Prioritize MD, but show TXT for backward compatibility
        return list(client_path.glob('*.md')) + list(client_path.glob('*.txt'))

    def create_custom_data_file(self, client_path, cod, ver='00', rev='R00', desc='PROPOSTA'):
        """
        Creates a data file with the specific naming convention (Markdown).
        """
        client_path = Path(client_path)
        if not client_path.exists():
            return None
        
        filename = f"02-{cod}_DOC_PC_{ver}_{rev}_{desc}.md"
        data_file = client_path / filename
        
        if data_file.exists():
            logger.warning(f"Arquivo já existe: {filename}")
            return data_file
        
        # Template content (Markdown Key: Value)
        # Reduced template relying on Centers of Truth (Inheritance)
        content = """@TEMPLATE: nome do arquivo template a ser utilizado
# DADOS ESPECÍFICOS DO DOCUMENTO
# (Dados do Cliente e Serviço são carregados automaticamente dos arquivos INFO)
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
        """
        Generates a document based on a template and a data file.
        """
        logger.info(f"Gerando documento do tipo {doc_type}...")
        
        # 1. Load Context Data (Centers of Truth)
        context_data = self._load_context_data(Path(data_path))
        
        # 2. Load Document Data
        doc_data = self._load_data(data_path)
        if not doc_data and not context_data:
            logger.error("Nenhum dado carregado (nem do arquivo nem do contexto).")
            return

        # 3. Merge (Document overrides Context)
        replacements = {**context_data, **doc_data}

        # Resolve operations
        self._resolve_operations(replacements)

        # Validate Keys
        missing_keys = self._validate_keys(template_path, replacements, doc_type)
        
        # Clean missing variables if configured
        if missing_keys and Config().clean_missing_variables:
            placeholder = Config().missing_variable_placeholder
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

    def _load_context_data(self, data_path):
        """
        Traverses up the directory tree from data_path to find INFO-*.md files.
        Returns merged data (Parent overrides Grandparent).
        """
        data = {}
        try:
            base_clients = Config().base_pasta_clientes
            current_dir = data_path.parent
            
            # Collect directories from base up to current
            dirs_to_check = []
            while current_dir != base_clients and current_dir != current_dir.parent:
                dirs_to_check.append(current_dir)
                current_dir = current_dir.parent
            
            # Reverse to process from top (Client) to bottom (Service)
            dirs_to_check.reverse()
            
            for folder in dirs_to_check:
                alias = folder.name
                # Find latest INFO file for this alias
                info_file = self._get_latest_info_file(folder, alias)
                if info_file:
                    logger.info(f"Carregando contexto de: {info_file.name}")
                    folder_data = self._parse_md_data(info_file)
                    data.update(folder_data)
                    
        except Exception as e:
            logger.warning(f"Erro ao carregar dados de contexto: {e}")
            
        return data

    def _get_latest_info_file(self, folder, alias):
        """
        Finds the latest version of COD_DOC_CD_VER_REV_INFO-{alias}.md
        """
        if not folder.exists():
            return None
            
        files = list(folder.glob(f"*_INFO-{alias}.md"))
        if not files:
            return None
            
        # Sort by name (lexicographically works for VER_REV if format is consistent)
        # 02-COD_DOC_CD_00_R00... vs 02-COD_DOC_CD_00_R01...
        files.sort(key=lambda f: f.name, reverse=True)
        return files[0]

    def validate_template_keys(self, template_path, data_path, doc_type):
        """
        Public method to validate keys before generation.
        """
        # Must load context here too to validate correctly
        context_data = self._load_context_data(Path(data_path))
        doc_data = self._load_data(data_path)
        replacements = {**context_data, **doc_data}
        
        return self._validate_keys(template_path, replacements, doc_type)

    def _validate_keys(self, template_path, replacements, doc_type):
        """
        Checks if keys used in the template exist in the replacements.
        Returns a list of missing keys.
        """
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
        except Exception as e:
            logger.warning(f"Não foi possível validar as chaves do template: {e}")
            return []

        missing_keys = [k for k in required_keys if k not in replacements]
        if missing_keys:
            logger.warning(f"CHAVES FALTANDO: {missing_keys}")
            
        return missing_keys

    def _log_generation(self, output_path, doc_type, template_path, data_path):
        """
        Logs the document generation event to a history file in the client's folder.
        """
        try:
            client_dir = Path(output_path).parent
            history_file = client_dir / 'history.log'
            
            from datetime import datetime
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
            import re
            found = re.findall(r'(?<![\w.])@[\w%]+(?!\.[a-z]{2,}\b)', text)
            keys_set.update(found)

    def _load_data(self, path):
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
        Resolves mathematical operations in the replacements values.
        """
        for _ in range(3): # Max depth 3
            for key, value in replacements.items():
                if isinstance(value, str) and '[calculo:' in value:
                    match = re.search(r'\[calculo:\s*(.+?)\]', value)
                    if match:
                        expression = match.group(1)
                        for k, v in replacements.items():
                            if k in expression and k != key:
                                try:
                                    val_str = str(v).strip().replace(',', '.').replace('%', '')
                                    if not val_str:
                                        float_val = 0.0
                                    else:
                                        clean_val = re.sub(r'[^\d.-]', '', val_str)
                                        float_val = float(clean_val) if clean_val else 0.0
                                        
                                    expression = expression.replace(k, str(float_val))
                                except:
                                    pass
                        try:
                            if not re.match(r'^[\d\.\-\+\*\/\(\)\s]+$', expression):
                                raise ValueError("Expressão contém caracteres inválidos")
                                
                            result = eval(expression)
                            replacements[key] = f"{result:.2f}".replace('.', ',')
                        except Exception as e:
                            logger.warning(f"Falha ao calcular {key}: {e}")
