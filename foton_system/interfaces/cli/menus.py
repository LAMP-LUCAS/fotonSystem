from foton_system.modules.clients.services import ClientService
from foton_system.modules.productivity.pomodoro import PomodoroTimer
from foton_system.modules.documents.services import DocumentService
from foton_system.core.logger import setup_logger

logger = setup_logger()

class MenuSystem:
    def __init__(self):
        self.client_service = ClientService()
        self.document_service = DocumentService()

    def display_main_menu(self):
        print("\n=== LAMP SYSTEM ===")
        print("1. Gerenciar Clientes")
        print("2. Gerenciar Serviços")
        print("3. Documentos")
        print("4. Produtividade")
        print("0. Sair")
        return input("Escolha uma opção: ")

    def display_clients_menu(self):
        print("\n--- Gerenciar Clientes ---")
        print("1. Sincronizar Base (Pastas -> DB)")
        print("2. Sincronizar Pastas (DB -> Pastas)")
        print("3. Criar Novo Cliente")
        print("0. Voltar")
        return input("Escolha uma opção: ")

    def display_services_menu(self):
        print("\n--- Gerenciar Serviços ---")
        print("1. Sincronizar Base (Pastas -> DB)")
        print("2. Sincronizar Pastas (DB -> Pastas)")
        print("0. Voltar")
        return input("Escolha uma opção: ")

    def display_documents_menu(self):
        print("\n--- Documentos ---")
        print("1. Gerar Proposta (PPTX)")
        print("2. Gerar Contrato (DOCX)")
        print("0. Voltar")
        return input("Escolha uma opção: ")

    def display_productivity_menu(self):
        print("\n--- Produtividade ---")
        print("1. Iniciar Pomodoro")
        print("0. Voltar")
        return input("Escolha uma opção: ")

    def run(self):
        while True:
            choice = self.display_main_menu()
            
            if choice == '1':
                self.handle_clients()
            elif choice == '2':
                self.handle_services()
            elif choice == '3':
                self.handle_documents()
            elif choice == '4':
                self.handle_productivity()
            elif choice == '0':
                print("Saindo...")
                sys.exit()
            else:
                print("Opção inválida.")

    def handle_clients(self):
        while True:
            choice = self.display_clients_menu()
            if choice == '1':
                self.client_service.sync_clients_db_from_folders()
            elif choice == '2':
                self.client_service.sync_client_folders_from_db()
            elif choice == '3':
                self.create_client_ui()
            elif choice == '0':
                break
            else:
                print("Opção inválida.")

    def handle_services(self):
        while True:
            choice = self.display_services_menu()
            if choice == '1':
                self.client_service.sync_services_db_from_folders()
            elif choice == '2':
                self.client_service.sync_service_folders_from_db()
            elif choice == '0':
                break
            else:
                print("Opção inválida.")

    def handle_documents(self):
        while True:
            choice = self.display_documents_menu()
            if choice == '1':
                self.generate_document_ui('pptx')
            elif choice == '2':
                self.generate_document_ui('docx')
            elif choice == '0':
                break
            else:
                print("Opção inválida.")

    def handle_productivity(self):
        while True:
            choice = self.display_productivity_menu()
            if choice == '1':
                self.start_pomodoro_ui()
            elif choice == '0':
                break
            else:
                print("Opção inválida.")

    def create_client_ui(self):
        print("\n--- Novo Cliente ---")
        nome = input("Nome do Cliente: ")
        alias = input("Alias (Apelido da Pasta): ")
        telefone = input("Telefone: ")
        
        data = {
            'NomeCliente': nome,
            'Alias': alias,
            'TelefoneCliente': telefone
        }
        
        try:
            self.client_service.create_client(data)
            print("Cliente criado com sucesso!")
        except Exception as e:
            print(f"Erro ao criar cliente: {e}")

    def generate_document_ui(self, doc_type):
        from foton_system.core.config import Config
        from pathlib import Path
        import tkinter as tk
        from tkinter import filedialog

        print(f"\n--- Gerar Documento ({doc_type.upper()}) ---")
        
        # 1. Select Client Folder via GUI
        print("Selecione a pasta do cliente na janela que abrirá...")
        root = tk.Tk()
        root.withdraw() # Hide main window
        root.attributes('-topmost', True) # Bring to front
        client_folder = filedialog.askdirectory(title="Selecione a Pasta do Cliente")
        root.destroy()

        if not client_folder:
            print("Nenhuma pasta selecionada.")
            return
        
        client_path = Path(client_folder)
        print(f"Pasta selecionada: {client_path}")

        # 2. Check/Create Data File Pipeline
        data_files = self.document_service.list_client_data_files(client_path)
        
        selected_file = None
        
        if data_files:
            print("\nArquivos de dados encontrados:")
            for i, f in enumerate(data_files):
                print(f"{i + 1}. {f.name}")
            print(f"{len(data_files) + 1}. Criar novo arquivo")
            
            try:
                choice = int(input("Escolha uma opção: "))
                if 1 <= choice <= len(data_files):
                    selected_file = data_files[choice - 1]
                elif choice == len(data_files) + 1:
                    selected_file = self._create_new_data_file_ui(client_path)
                else:
                    print("Opção inválida.")
                    return
            except ValueError:
                print("Entrada inválida.")
                return
        else:
            print("\nNenhum arquivo de dados encontrado.")
            create = input("Deseja criar um novo arquivo? (S/N): ").upper()
            if create == 'S':
                selected_file = self._create_new_data_file_ui(client_path)
            else:
                return

        if not selected_file:
            return

        print(f"Arquivo selecionado: {selected_file.name}")
        
        # Option to edit data file?
        edit = input("Deseja abrir o arquivo de dados para edição antes de continuar? (S/N): ").upper()
        if edit == 'S':
            import os
            os.startfile(selected_file)
            input("Pressione Enter após salvar e fechar o arquivo de dados...")

        # 3. Select Template
        templates = self.document_service.list_templates(doc_type)
        if not templates:
            print("Nenhum template encontrado.")
            return

        print("\nSelecione o Template:")
        template_name = self._select_from_list(templates)
        if not template_name:
            return
        
        template_path = Config().templates_path / template_name

        # 4. Output Path (same as client folder)
        default_output = f"Proposta_{client_path.name}"
        output_name = input(f"Nome do arquivo de saída (padrão: {default_output}): ") or default_output
        if doc_type == 'pptx' and not output_name.endswith('.pptx'):
            output_name += '.pptx'
        elif doc_type == 'docx' and not output_name.endswith('.docx'):
            output_name += '.docx'
            
        output_path = client_path / output_name
        
        try:
            self.document_service.generate_document(str(template_path), str(selected_file), str(output_path), doc_type)
            print(f"Documento gerado com sucesso em: {output_path}")
            
            # Open folder
            import os
            os.startfile(client_path)
            
        except Exception as e:
            print(f"Erro ao gerar documento: {e}")

    def _select_from_list(self, items):
        for i, item in enumerate(items):
            print(f"{i + 1}. {item}")
        
        try:
            choice = int(input("Digite o número da opção: "))
            if 1 <= choice <= len(items):
                return items[choice - 1]
            else:
                print("Opção inválida.")
                return None
        except ValueError:
            print("Entrada inválida.")
            return None

    def _create_new_data_file_ui(self, client_path):
        print("\n--- Criar Novo Arquivo de Dados ---")
        print("Padrão: 02-{COD}_DOC_PC_{VER}_{REV}_{DESC}.txt")
        
        cod = input("Código do Serviço (COD) [ex: 001]: ")
        if not cod:
            print("Código é obrigatório.")
            return None
            
        ver = input("Versão (VER) [padrão: 00]: ") or "00"
        rev = input("Revisão (REV) [padrão: R00]: ") or "R00"
        desc = input("Descrição (DESC) [padrão: PROPOSTA]: ") or "PROPOSTA"
        
        return self.document_service.create_custom_data_file(client_path, cod, ver, rev, desc)

    def start_pomodoro_ui(self):
        try:
            work = float(input("Tempo de trabalho (min): ") or 25)
            short = float(input("Pausa curta (min): ") or 5)
            long = float(input("Pausa longa (min): ") or 15)
            cycles = int(input("Ciclos: ") or 4)
            
            timer = PomodoroTimer(work, short, long, cycles)
            timer.run()
        except ValueError:
            print("Valores inválidos.")
