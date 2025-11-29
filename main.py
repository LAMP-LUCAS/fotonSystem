import os
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import win32com.client
import logging

logging.basicConfig(
    filename='main.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w',
    encoding='utf-8'
)

# Caminho absoluto do Python (ajuste conforme o seu ambiente)
python_exe = r"C:\Users\Lucas\AppData\Local\Programs\Python\Python312\python.exe"  

pasta = r"C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\ADM\lamp\scripts"

# Função para resolver o caminho de um atalho .lnk (somente no Windows)
def resolver_atalho(caminho_atalho):
    logging.info(f'resolvendo caminho: {caminho_atalho}')
    shell = win32com.client.Dispatch("WScript.Shell")
    try:
        atalho = shell.CreateShortcut(caminho_atalho)
        destino = atalho.Targetpath
        logging.info(f'Atalho apontando para: {destino}')
        return destino
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível resolver o atalho: {str(e)}")
        return None

# Função para executar o script selecionado em um terminal separado
def executar_script(script):
    caminho_completo = os.path.join(pasta, script)
    logging.info(f'Caminho 1 - {caminho_completo}')
    
    # Se for um arquivo de atalho (.lnk), resolva o destino real
    if caminho_completo.endswith('.lnk') and os.name == 'nt':
        caminho_completo = resolver_atalho(caminho_completo)
        logging.info(f'Caminho 2 - {caminho_completo}')
        if not caminho_completo:
            logging.info(f'Não foi possível resolver o atalho: {script}')
            return  # Se não conseguiu resolver, não continua
        
        # Verificar se o caminho resolvido é um script Python válido
        if not os.path.exists(caminho_completo) or not caminho_completo.endswith(".py"):
            messagebox.showerror("Erro", "O atalho não aponta para um script Python válido.")
            return  # Parar se o atalho não resolver para um script Python    
    
    # Escapar o caminho para lidar com espaços
    caminho_completo = f'"{caminho_completo}"'
    
    try:
        if os.name == 'nt':  # Windows
            logging.info(f'Caminho 3 - {python_exe} {caminho_completo}')
            # Colocando o caminho dentro de aspas para lidar com espaços
            subprocess.Popen(f'start cmd /k "{python_exe} {caminho_completo}"', shell=True)
        else:  # Linux/MacOS
            subprocess.Popen(['gnome-terminal', '--', 'python3', caminho_completo])
        
        messagebox.showinfo("Sucesso", f"{script} foi iniciado em um novo terminal!")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao iniciar {script}: {str(e)}")

# Função para listar scripts e atalhos na pasta "scripts"
def listar_scripts():
    caminho = pasta
    scripts = []
    for f in os.listdir(caminho):
        full_path = os.path.join(caminho, f)
        if f.endswith('.py') or (f.endswith('.lnk') and os.name == 'nt') or (os.path.islink(full_path) or os.path.isfile(full_path)):
            scripts.append(f)
    return scripts

# Função para cadastrar um novo script
def cadastrar_script():
    nome_script = simpledialog.askstring("Novo Script", "Digite o nome do script (sem extensão):")
    if nome_script:
        conteudo_script = simpledialog.askstring("Conteúdo do Script", "Insira o conteúdo do script:")
        if conteudo_script:
            caminho_completo = os.path.join(pasta, f"{nome_script}.py")
            logging.info(f'caminho em cadastrar: {caminho_completo}')
            try:
                with open(caminho_completo, 'w') as arquivo:
                    arquivo.write(conteudo_script)
                messagebox.showinfo("Sucesso", f"Script '{nome_script}.py' criado com sucesso!")
                atualizar_lista_scripts()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível criar o script: {str(e)}")

# Função para adicionar atalho para um script existente
def adicionar_atalho():
    caminho_script = filedialog.askopenfilename(title="Selecione o Script", filetypes=[("Python Scripts", "*.py")])
    if caminho_script:
        nome_atalho = os.path.basename(caminho_script)
        caminho_atalho = os.path.join(pasta, nome_atalho)
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            atalho = shell.CreateShortcut(caminho_atalho + ".lnk")
            atalho.Targetpath = caminho_script
            atalho.save()
            messagebox.showinfo("Sucesso", f"Atalho para '{nome_atalho}' criado com sucesso!")
            atualizar_lista_scripts()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível criar o atalho: {str(e)}")

# Função para atualizar a lista de scripts na interface
def atualizar_lista_scripts():
    for widget in frame_scripts.winfo_children():
        widget.destroy()
    
    scripts = listar_scripts()
    
    for script in scripts:
        button = tk.Button(frame_scripts, text=script, command=lambda s=script: executar_script(s))
        button.pack(pady=5)

# Configuração da interface Tkinter
def criar_interface():
    global frame_scripts
    
    root = tk.Tk()
    root.title("Executar Scripts")
    root.geometry("400x400")

    label = tk.Label(root, text="Selecione um script para executar:")
    label.pack(pady=10)
    
    frame_scripts = tk.Frame(root)
    frame_scripts.pack(pady=10)
    
    btn_novo_script = tk.Button(root, text="Cadastrar Novo Script", command=cadastrar_script)
    btn_novo_script.pack(pady=5)
    
    btn_novo_atalho = tk.Button(root, text="Adicionar Atalho para Script", command=adicionar_atalho)
    btn_novo_atalho.pack(pady=5)
    
    atualizar_lista_scripts()

    root.mainloop()

if __name__ == "__main__":
    criar_interface()
