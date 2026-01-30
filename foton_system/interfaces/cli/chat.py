import sys
import cmd
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.sync.sync_service import SyncService

class FotonChat(cmd.Cmd):
    intro = 'Bem-vindo ao Foton Chat. Digite "ajuda" ou "proposta".'
    prompt = '(Foton) > '

    def do_sync(self, arg):
        'Sincroniza os dados das pastas com o Excel Mestre: SYNC'
        print("Sincronizando...")
        try:
            SyncService().sync_dashboard()
            print("Sincronização concluída!")
        except Exception as e:
            print(f"Erro: {e}")

    def do_proposta(self, arg):
        'Inicia o assistente de proposta: PROPOSTA'
        print("Assistente de Proposta iniciado...")
        # Aqui conectaria com o DocumentService
        print("Funcionalidade em desenvolvimento: chame via run_gen.py por enquanto.")

    def do_sair(self, arg):
        'Sai do chat: SAIR'
        print('Até logo!')
        return True

if __name__ == '__main__':
    FotonChat().cmdloop()
