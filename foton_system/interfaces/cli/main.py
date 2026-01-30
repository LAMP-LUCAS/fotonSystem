from foton_system.interfaces.cli.menus import MenuSystem
from foton_system.modules.shared.infrastructure.services.update_service import UpdateChecker

def main():
    # Check for updates
    try:
        UpdateChecker.check_for_updates() # O serviço já faz o log do status
    except Exception:
        pass # Don't block startup on update error

    menu = MenuSystem()
    menu.run()

if __name__ == "__main__":
    main()
