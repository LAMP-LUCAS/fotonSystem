import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from foton_system.modules.documents.docx_handler import DOCXHandler
from foton_system.modules.documents.services import DocumentService

def debug_docx():
    template_path = r"C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\ADM\KIT DOC\03-COD_DOC_CT_00_R00_CONTRATO-PROJETO.docx"
    data_path = r"c:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\CLIENTES\ED_RIO-AMAZONAS\ACEITE-CBMGO\02-EDRA_DOC_PC_00_R00_ACEITE-CBMGO.txt"
    output_path = "debug_output.docx"

    print(f"Template: {template_path}")
    print(f"Data: {data_path}")

    service = DocumentService()
    replacements = service._load_data(data_path)
    service._resolve_operations(replacements)
    
    print(f"Loaded {len(replacements)} keys.")
    # print(replacements)

    handler = DOCXHandler()
    doc = handler.load_document(template_path)
    
    print("\n--- Inspecting Document Content ---")
    
    found_keys = set()
    def inspect_paragraph(p, context="Body"):
        text = p.text
        if "@" in text:
            # Simple regex to find keys
            import re
            keys = re.findall(r'@[\w%]+', text)
            for k in keys:
                found_keys.add(k)

    # Body
    for p in doc.paragraphs:
        inspect_paragraph(p, "Body")
        
    # Tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    inspect_paragraph(p, "Table")
                    
    # Shapes (Inline)
    for shape in doc.inline_shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                inspect_paragraph(p, "InlineShape")

    # Headers/Footers
    for section in doc.sections:
        for p in section.header.paragraphs:
            inspect_paragraph(p, "Header")
        for p in section.footer.paragraphs:
            inspect_paragraph(p, "Footer")
            
    # Anchored Shapes (approximate check)
    # This requires more complex XML parsing which we already have in handler, 
    # but for debug let's just rely on what we found so far.
            
    print("\n--- Keys Found in Template ---")
    for k in sorted(found_keys):
        print(k)
        
    print("\n--- Keys in Data File ---")
    for k in sorted(replacements.keys()):
        print(k)
            
    print("\n--- Attempting Replacement ---")
    handler.replace_text(doc, replacements)
    handler.save_document(doc, output_path)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    debug_docx()
