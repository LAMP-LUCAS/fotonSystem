import sys
import os

# Ensure the parent directory is in the python path so we can import foton_system
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from foton_system.interfaces.cli.main import main

if __name__ == "__main__":
    main()
