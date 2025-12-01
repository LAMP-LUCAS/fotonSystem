import os
from pptx import Presentation
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.documents.application.ports.document_service_port import DocumentServicePort

logger = setup_logger()

class PythonPPTXAdapter(DocumentServicePort):
    def __init__(self):
        pass

    def load_document(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo PPTX não encontrado: {path}")
        return Presentation(path)

    def save_document(self, document, path: str):
        try:
            document.save(path)
            logger.info(f"Apresentação salva em: {path}")
        except Exception as e:
            logger.error(f"Erro ao salvar apresentação: {e}")
            raise

    def replace_text(self, document, replacements: dict):
        """
        Replaces keys with values in a PowerPoint presentation.
        """
        logger.info('Iniciando substituição de textos no PPTX...')
        
        for slide in document.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    self._replace_in_text_frame(shape.text_frame, replacements)

                if shape.has_table:
                    self._replace_in_table(shape.table, replacements)
        
        logger.info('Substituição de textos concluída.')
        return document

    def _replace_in_text_frame(self, text_frame, replacements):
        for paragraph in text_frame.paragraphs:
            for run in paragraph.runs:
                run.text = self._replace_keys_in_text(run.text, replacements)

    def _replace_in_table(self, table, replacements):
        for row in table.rows:
            for cell in row.cells:
                self._replace_in_text_frame(cell.text_frame, replacements)

    def _replace_keys_in_text(self, text, replacements):
        import re
        # Sort keys by length (descending) to avoid partial replacement issues
        sorted_keys = sorted(replacements.keys(), key=len, reverse=True)
        
        for key in sorted_keys:
            if key in text:
                # Use regex to ensure we don't replace inside words/emails
                pattern = r'(?<![\w.])' + re.escape(key) + r'(?!\.[a-z]{2,}\b)'
                new_val = str(replacements[key])
                text = re.sub(pattern, new_val, text)
                
        return text
