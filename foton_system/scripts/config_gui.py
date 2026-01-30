import tkinter as tk
from tkinter import filedialog, messagebox
import json
import sys
from pathlib import Path

# Setup paths
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent.parent
sys.path.append(str(root_dir))

from foton_system.modules.shared.infrastructure.config.config import Config

class ConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Foton System - Configuração")
        self.root.geometry("600x450")
        self.config = Config()
        self.entries = {}
        
        tk.Label(root, text="Painel de Controle", font=("Arial", 14, "bold")).pack(pady=10)
        form_frame = tk.Frame(root)
        form_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.fields = [
            ("Pasta de Clientes", "caminho_pastaClientes", True),
            ("Pasta de Templates", "caminho_templates", True),
            ("Arquivo Base Dados (Excel)", "caminho_baseDados", False),
        ]
        for label_text, key, is_folder in self.fields:
            self.create_field(form_frame, label_text, key, is_folder)

        tk.Label(form_frame, text="Opções Avançadas", font=("Arial", 10, "bold")).pack(pady=(15, 5), anchor="w")
        self.clean_vars = tk.BooleanVar(value=self.config.get("clean_missing_variables", True))
        tk.Checkbutton(form_frame, text="Limpar variáveis não encontradas", variable=self.clean_vars).pack(anchor="w")

        tk.Button(root, text="Salvar Configurações", command=self.save, bg="#4CAF50", fg="white", height=2).pack(pady=20, fill="x", padx=20)

    def create_field(self, parent, label, key, is_folder):
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=5)
        tk.Label(frame, text=label, width=20, anchor="w").pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        entry.insert(0, str(self.config.get(key, "")))
        self.entries[key] = entry
        btn_cmd = lambda: self.browse_folder(entry) if is_folder else self.browse_file(entry)
        tk.Button(frame, text="📂", command=btn_cmd).pack(side="right")

    def browse_folder(self, entry):
        path = filedialog.askdirectory()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def browse_file(self, entry):
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def save(self):
        try:
            for key, entry in self.entries.items():
                val = entry.get()
                self.config.set(key, val)
            self.config.set("clean_missing_variables", self.clean_vars.get())
            self.config.save()
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigApp(root)
    root.mainloop()
