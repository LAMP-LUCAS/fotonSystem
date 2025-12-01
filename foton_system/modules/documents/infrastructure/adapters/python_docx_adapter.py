import os
from docx import Document
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.documents.application.ports.document_service_port import DocumentServicePort

logger = setup_logger()

class PythonDocxAdapter(DocumentServicePort):
    def __init__(self):
        pass

    def load_document(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo DOCX não encontrado: {path}")
        return Document(path)

    def save_document(self, document, path: str):
        try:
            document.save(path)
            logger.info(f"Documento salvo em: {path}")
        except Exception as e:
            logger.error(f"Erro ao salvar documento: {e}")
            raise

    def replace_text(self, document, replacements: dict):
        """
        Replaces keys with values in a Word document.
        """
        logger.info('Iniciando substituição de textos no DOCX...')
        
        # Replace in paragraphs
        for paragraph in document.paragraphs:
            self._replace_in_paragraph(paragraph, replacements)

        # Replace in tables
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._replace_in_paragraph(paragraph, replacements)
        
        # Replace in inline shapes (text boxes in body)
        for shape in document.inline_shapes:
            if shape.has_text_frame:
                self._replace_in_text_frame(shape.text_frame, replacements)

        # Replace in headers and footers (including anchored shapes)
        for section in document.sections:
            self._replace_in_header_footer(section.header, replacements)
            self._replace_in_header_footer(section.footer, replacements)

        logger.info('Substituição de textos concluída.')
        return document

    def _replace_in_header_footer(self, header_footer, replacements):
        if header_footer:
            for paragraph in header_footer.paragraphs:
                self._replace_in_paragraph(paragraph, replacements)
            for table in header_footer.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            self._replace_in_paragraph(paragraph, replacements)
            
            # Handle anchored shapes in header/footer
            self._process_anchored_shapes(header_footer._element, replacements)

    def _replace_in_paragraph(self, paragraph, replacements):
        # Consolidate runs to fix split keys (e.g. ["@", "key"])
        self._consolidate_runs(paragraph)
        
        for run in paragraph.runs:
            if run.text:
                run.text = self._replace_keys_in_text(run.text, replacements)

    def _consolidate_runs(self, paragraph):
        """
        Consolidates runs in a paragraph to ensure keys aren't split across runs.
        """
        # Check if there's any '@' in the paragraph text first
        if '@' not in paragraph.text:
            return
        
        text = paragraph.text
        # Only consolidate if it looks like a key might be present
        if '@' in text:
            # Check if we actually have multiple runs
            if len(paragraph.runs) > 1:
                # Collect all text
                full_text = "".join(run.text for run in paragraph.runs)
                
                # Set first run text
                paragraph.runs[0].text = full_text
                
                # Clear other runs
                for run in paragraph.runs[1:]:
                    run.text = ""

    def _replace_keys_in_text(self, text, replacements):
        import re
        # Sort keys by length (descending) to avoid partial replacement issues if keys share prefixes
        sorted_keys = sorted(replacements.keys(), key=len, reverse=True)
        
        for key in sorted_keys:
            if key in text:
                # Use regex to ensure we don't replace inside words/emails
                pattern = r'(?<![\w.])' + re.escape(key) + r'(?!\.[a-z]{2,}\b)'
                new_val = str(replacements[key])
                text = re.sub(pattern, new_val, text)
                
        return text

    def _replace_in_shapes(self, shapes, replacements):
        for shape in shapes:
            if shape.has_text_frame:
                self._replace_in_text_frame(shape.text_frame, replacements)

    def _replace_in_text_frame(self, text_frame, replacements):
        for paragraph in text_frame.paragraphs:
            self._replace_in_paragraph(paragraph, replacements)

    def _process_anchored_shapes(self, element, replacements):
        """
        Traverses XML to find anchored text boxes (w:drawing) and replaces text.
        """
        if hasattr(element, "xpath"):
            paragraphs = element.xpath('.//w:txbxContent/w:p')
            for p_element in paragraphs:
                runs = p_element.xpath('.//w:r')
                for run in runs:
                    texts = run.xpath('.//w:t')
                    for t in texts:
                        if t.text:
                            original_text = t.text
                            new_text = self._replace_keys_in_text(original_text, replacements)
                            if original_text != new_text:
                                t.text = new_text
