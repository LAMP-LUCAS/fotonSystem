"""
TUI Form Filler Use Case - Orquestra o fluxo de preenchimento TUI de alta performance.
"""

import shutil
from pathlib import Path
from colorama import Fore, Style
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
        if action == "save" or action == "save_as":
            target_path = self.file_path
            
            if action == "save_as":
                from datetime import datetime
                suffix = datetime.now().strftime("%Y%m%d_%H%M")
                default_name = f"{self.file_path.stem}_{suffix}.md"
                
                print(f"\n{Fore.CYAN}--- SALVAR COMO ---{Style.RESET_ALL}")
                new_name = input(f"Digite o novo nome (Vazio para {default_name}): ").strip()
                if not new_name:
                    new_name = default_name
                if not new_name.endswith(".md"):
                    new_name += ".md"
                
                target_path = self.file_path.parent / new_name
            else:
                # Criar backup antes de sobrescrever
                try:
                    bak_path = self.file_path.with_suffix(self.file_path.suffix + ".bak")
                    shutil.copy2(self.file_path, bak_path)
                except (IOError, OSError): pass

            try:
                # Gerar e salvar novo MD
                new_md = self.session.generate_markdown()
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(new_md)
                
                if action == "save_as":
                    print(f"\n✅ {Fore.GREEN}Nova versão criada: {target_path.name}{Style.RESET_ALL}")
                return True
            except Exception as e:
                print(f"❌ Erro ao salvar arquivo: {e}")
                return False
            
        return False
