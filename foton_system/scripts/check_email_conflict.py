import sys
import os
import re
from pathlib import Path

# Add project root to path
# Add project root to path (3 levels up: scripts -> foton_system -> lamp)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from foton_system.modules.documents.docx_handler import DOCXHandler
from foton_system.modules.documents.pptx_handler import PPTXHandler

def check_email_conflict():
    templates_dir = Path(r"C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\ADM\KIT DOC")
    docx_handler = DOCXHandler()
    pptx_handler = PPTXHandler()
    
    target_keys = ['@ARQLAMP', '@arqlamp']
    
    print(f"Checking context for {target_keys} in: {templates_dir}\n")
    
    for file_path in templates_dir.glob('*'):
        if file_path.name.startswith('~$'): continue

        def check_text(text, filename, source):
            if not text: return
            for key in target_keys:
                if key in text:
                    # Find the context (surrounding chars)
                    start = max(0, text.find(key) - 10)
                    end = min(len(text), text.find(key) + len(key) + 10)
                    snippet = text[start:end]
                    print(f"[{filename}] ({source}): ...{snippet.strip()}...")
                    
                    # Check if it looks like an email
                    # Preceded by alphanumeric?
                    idx = text.find(key)
                    if idx > 0 and text[idx-1].isalnum():
                        print(f"  -> WARNING: Looks like part of an email or word!")
                    else:
                        print(f"  -> Looks like a standalone key.")

        if file_path.suffix == '.docx':
            try:
                doc = docx_handler.load_document(str(file_path))
                for p in doc.paragraphs: check_text(p.text, file_path.name, "Body")
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for p in cell.paragraphs: check_text(p.text, file_path.name, "Table")
                for section in doc.sections:
                    for p in section.header.paragraphs: check_text(p.text, file_path.name, "Header")
                    for p in section.footer.paragraphs: check_text(p.text, file_path.name, "Footer")
            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")

        elif file_path.suffix == '.pptx':
            try:
                prs = pptx_handler.load_presentation(str(file_path))
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if shape.has_text_frame:
                            for p in shape.text_frame.paragraphs:
                                for run in p.runs: check_text(run.text, file_path.name, "Slide")
                        if shape.has_table:
                            for row in shape.table.rows:
                                for cell in row.cells:
                                    if cell.text_frame:
                                        for p in cell.text_frame.paragraphs:
                                            for run in p.runs: check_text(run.text, file_path.name, "Table")
            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")

if __name__ == "__main__":
    check_email_conflict()
