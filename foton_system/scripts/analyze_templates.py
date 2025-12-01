import sys
import os
import re
from pathlib import Path
from collections import defaultdict
import pandas as pd

# Add project root to path
# Add project root to path (3 levels up: scripts -> foton_system -> lamp)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from foton_system.modules.documents.docx_handler import DOCXHandler
from foton_system.modules.documents.pptx_handler import PPTXHandler

def analyze_templates():
    templates_dir = Path(r"C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\ADM\KIT DOC")
    data_template_path = templates_dir / "02-COD_DOC_PC_00_R00_PROPOSTA.txt"
    
    docx_handler = DOCXHandler()
    pptx_handler = PPTXHandler()
    
    # 1. Load Standard Keys from TXT
    standard_keys = set()
    if data_template_path.exists():
        with open(data_template_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(';')
                if len(parts) >= 1 and parts[0].startswith('@'):
                    standard_keys.add(parts[0])
    
    print(f"Standard Keys in TXT ({len(standard_keys)}):")
    print(", ".join(sorted(standard_keys)))
    print("-" * 50)

    pptx_keys = set()
    docx_keys = set()
    
    pptx_files = []
    docx_files = []

    print(f"Analyzing templates in: {templates_dir}\n")
    
    for file_path in templates_dir.glob('*'):
        if file_path.name.startswith('~$'): continue # Skip temp files

        if file_path.suffix == '.docx':
            docx_files.append(file_path.name)
            try:
                doc = docx_handler.load_document(str(file_path))
                
                def extract_keys(text):
                    if text and '@' in text:
                        found = re.findall(r'@[\w%]+', text)
                        docx_keys.update(found)
                
                # Scan everything
                for p in doc.paragraphs: extract_keys(p.text)
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for p in cell.paragraphs: extract_keys(p.text)
                for shape in doc.inline_shapes:
                    if shape.has_text_frame:
                        for p in shape.text_frame.paragraphs: extract_keys(p.text)
                for section in doc.sections:
                    for p in section.header.paragraphs: extract_keys(p.text)
                    for p in section.footer.paragraphs: extract_keys(p.text)
                    # Anchored shapes check (simple regex on XML for speed/coverage)
                    xml = section.header._element.xml
                    extract_keys(xml)
                    xml = section.footer._element.xml
                    extract_keys(xml)

            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")

        elif file_path.suffix == '.pptx':
            pptx_files.append(file_path.name)
            try:
                prs = pptx_handler.load_presentation(str(file_path))
                
                def extract_keys(text):
                    if text and '@' in text:
                        found = re.findall(r'@[\w%]+', text)
                        pptx_keys.update(found)

                for slide in prs.slides:
                    for shape in slide.shapes:
                        if shape.has_text_frame:
                            for p in shape.text_frame.paragraphs:
                                for run in p.runs: extract_keys(run.text)
                        if shape.has_table:
                            for row in shape.table.rows:
                                for cell in row.cells:
                                    if cell.text_frame:
                                        for p in cell.text_frame.paragraphs:
                                            for run in p.runs: extract_keys(run.text)

            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")

    print("\n--- COMPARISON REPORT ---\n")
    
    print(f"PROPOSALS (PPTX) - {len(pptx_files)} files analyzed")
    missing_in_pptx = standard_keys - pptx_keys
    extra_in_pptx = pptx_keys - standard_keys
    print(f"Matching Keys: {len(standard_keys.intersection(pptx_keys))}")
    # print(f"Keys in TXT but NOT in PPTX: {missing_in_pptx}") # Not necessarily an error
    print(f"Keys in PPTX but NOT in TXT (Potential Errors): {extra_in_pptx}")
    
    print("\n" + "="*30 + "\n")

    print(f"CONTRACTS (DOCX) - {len(docx_files)} files analyzed")
    missing_in_docx = standard_keys - docx_keys
    extra_in_docx = docx_keys - standard_keys
    print(f"Matching Keys: {len(standard_keys.intersection(docx_keys))}")
    print(f"Keys in DOCX but NOT in TXT (Potential Errors): {extra_in_docx}")

    print("\n--- DETAILED MISMATCHES (DOCX) ---")
    for k in sorted(extra_in_docx):
        print(f"  {k}")

if __name__ == "__main__":
    analyze_templates()
