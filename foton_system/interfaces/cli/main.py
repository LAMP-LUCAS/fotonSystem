from foton_system.interfaces.cli.menus import MenuSystem
from foton_system.infrastructure.update_checker import UpdateChecker

def main():
    # Check for updates
    try:
        checker = UpdateChecker()
        checker.prompt_update()
    except Exception as e:
        pass # Don't block startup on update error

    menu = MenuSystem()
    menu.run()

if __name__ == "__main__":
    main()
