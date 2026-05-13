"""
TUI Form Filler Use Case - Orquestra o fluxo de preenchimento TUI de alta performance.
"""

import shutil
from pathlib import Path
from foton_system.modules.documents.domain.models.form_session import FormSession
from foton_system.interfaces.cli.views.form_view import TUIFormView

class TUIFormFillerUseCase:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.session = FormSession()

    def execute(self) -> bool:
        """Executa o processo de preenchimento interativo."""
        if not self.file_path.exists():
            return False

        # 1. Carregar e Parsear (Instantâneo)
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.session.parse_markdown(content)
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
            return False
        
        # 2. Iniciar View (Loop de Interface Terminal)
        view = TUIFormView(self.session, title=f"Ficha: {self.file_path.name}")
        action = view.run_loop()
        
        # 3. Processar Ação Final
        if action == "save":
            try:
                # Criar backup antes de salvar
                bak_path = self.file_path.with_suffix(self.file_path.suffix + ".bak")
                shutil.copy2(self.file_path, bak_path)
                
                # Gerar e salvar novo MD
                new_md = self.session.generate_markdown()
                with open(self.file_path, "w", encoding="utf-8") as f:
                    f.write(new_md)
                return True
            except Exception as e:
                print(f"❌ Erro ao salvar arquivo: {e}")
                return False
            
        return False
