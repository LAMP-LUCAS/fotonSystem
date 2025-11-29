import os
import re
import json
from pathlib import Path
from foton_system.core.config import Config
from foton_system.core.logger import setup_logger
from foton_system.modules.documents.pptx_handler import PPTXHandler
from foton_system.modules.documents.docx_handler import DOCXHandler

logger = setup_logger()

class DocumentService:
    def __init__(self):
        self.pptx_handler = PPTXHandler()
        self.docx_handler = DOCXHandler()

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
        Lists all .txt and .json files in the templates directory (or a specific data dir).
        For now, using templates_path as a default location for data files too, 
        or we could add a new config for 'data_path'.
        """
        data_dir = Config().templates_path
        if not data_dir.exists():
            return []
        
        files = list(data_dir.glob('*.txt')) + list(data_dir.glob('*.json'))
        return [f.name for f in files]

    def list_client_data_files(self, client_path):
        """
        Lists all .txt files in the client directory.
        """
        client_path = Path(client_path)
        if not client_path.exists():
            return []
        return list(client_path.glob('*.txt'))

    def create_custom_data_file(self, client_path, cod, ver='00', rev='R00', desc='PROPOSTA'):
        """
        Creates a data file with the specific naming convention:
        02-{COD}_DOC_PC_{VER}_{REV}_{DESC}.txt
        """
        client_path = Path(client_path)
        if not client_path.exists():
            return None
        
        filename = f"02-{cod}_DOC_PC_{ver}_{rev}_{desc}.txt"
        data_file = client_path / filename
        
        if data_file.exists():
            logger.warning(f"Arquivo já existe: {filename}")
            return data_file
        
        # Template content (Expanded based on analysis)
        content = """@TEMPLATE;nome do arquivo template a ser utilizado
#DADOS BÁSICOS
@DataAtual;
#DADOS DO CLIENTE
@dataProposta;
@nomeCliente;
@enderecoCliente;
@cpfCnpjCliente;
@telefoneCliente;
@emailCliente;
@NomeCompleto;
@CpfCnpj;
#DADOS DO SERVIÇO
@anoProjeto;
@demandaProposta;
@areaTotal;
@detalhesProposta;
@valorProposta;
@modalidade;
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
        
        # Load data
        replacements = self._load_data(data_path)
        if not replacements:
            logger.error("Nenhum dado carregado.")
            return

        # Resolve operations
        self._resolve_operations(replacements)

        # Validate Keys
        self._validate_keys(template_path, replacements, doc_type)

        if doc_type == 'pptx':
            presentation = self.pptx_handler.load_presentation(template_path)
            presentation = self.pptx_handler.replace_text(presentation, replacements)
            self.pptx_handler.save_presentation(presentation, output_path)
        
        elif doc_type == 'docx':
            document = self.docx_handler.load_document(template_path)
            document = self.docx_handler.replace_text(document, replacements)
            self.docx_handler.save_document(document, output_path)
        
        else:
            logger.error(f"Tipo de documento desconhecido: {doc_type}")

    def _validate_keys(self, template_path, replacements, doc_type):
        """
        Checks if keys used in the template exist in the replacements.
        """
        required_keys = set()
        try:
            if doc_type == 'docx':
                # Quick scan for keys in docx (simplified)
                # For a robust check we'd need to use the handler's logic, 
                # but reading the file as text/xml is faster for a check.
                # However, let's use the handler since we have it.
                doc = self.docx_handler.load_document(template_path)
                # We can't easily extract all keys without iterating everything again.
                # Let's do a simple iteration.
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
                prs = self.pptx_handler.load_presentation(template_path)
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if shape.has_text_frame:
                            for p in shape.text_frame.paragraphs:
                                self._extract_keys_from_text(p.text, required_keys)
        except Exception as e:
            logger.warning(f"Não foi possível validar as chaves do template: {e}")
            return

        missing_keys = [k for k in required_keys if k not in replacements]
        if missing_keys:
            logger.warning(f"CHAVES FALTANDO: As seguintes chaves estão no template mas não no arquivo de dados: {missing_keys}")
            print(f"\n[AVISO] Chaves faltando no arquivo de dados: {missing_keys}")
            print("O documento será gerado, mas essas chaves não serão substituídas.\n")

    def _extract_keys_from_text(self, text, keys_set):
        if text and '@' in text:
            import re
            # Regex explanation:
            # (?<![\w.])      : Lookbehind - ensure not preceded by word char or dot (email local part)
            # @[\w%]+         : Match @ followed by word chars or %
            # (?!\.[a-z]{2,}) : Lookahead - ensure not followed by .com, .br, etc.
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

    def _resolve_operations(self, replacements):
        """
        Resolves mathematical operations in the replacements values.
        Format: [calculo: @key1 * @key2]
        """
        # Simple iterative resolution
        for _ in range(3): # Max depth 3
            for key, value in replacements.items():
                if isinstance(value, str) and '[calculo:' in value:
                    match = re.search(r'\[calculo:\s*(.+?)\]', value)
                    if match:
                        expression = match.group(1)
                        # Replace keys in expression
                        for k, v in replacements.items():
                            if k in expression and k != key:
                                try:
                                    # Try to convert to float for calculation
                                    # Handle empty or invalid values by defaulting to 0
                                    val_str = str(v).strip().replace(',', '.').replace('%', '')
                                    if not val_str:
                                        float_val = 0.0
                                    else:
                                        # Remove non-numeric chars except dot and minus
                                        clean_val = re.sub(r'[^\d.-]', '', val_str)
                                        float_val = float(clean_val) if clean_val else 0.0
                                        
                                    expression = expression.replace(k, str(float_val))
                                except:
                                    # If replacement fails, leave key (will likely cause eval error)
                                    pass
                        try:
                            # Safe eval? Well, it's a local tool.
                            # Ensure expression only contains allowed chars
                            if not re.match(r'^[\d\.\-\+\*\/\(\)\s]+$', expression):
                                raise ValueError("Expressão contém caracteres inválidos")
                                
                            result = eval(expression)
                            # Format result (2 decimal places)
                            replacements[key] = f"{result:.2f}".replace('.', ',')
                        except Exception as e:
                            logger.warning(f"Falha ao calcular {key}: {e}")
