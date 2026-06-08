"""
Entry-point module for ``python -m foton_system``.
Supports --mcp, --tui, --sandbox modes.
"""
from foton_system.main import safety_entry

if __name__ == "__main__":
    safety_entry()
