"""
UI Provider Abstraction Layer

Provides interface for UI interactions with two implementations:
- TUIProvider: Terminal-based (text input, listing selection)
- GUIProvider: Tkinter-based (file dialogs, windows)

This allows the system to run in headless/terminal-only environments
or with full GUI support depending on configuration.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List
import os


class UIProvider(ABC):
    """
    Abstract interface for user interface interactions.
    
    Implementations can be TUI (terminal) or GUI (tkinter) based.
    """
    
    @abstractmethod
    def select_directory(self, title: str, initial_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Prompt user to select a directory.
        
        Args:
            title: Title for the selection dialog/prompt
            initial_dir: Starting directory for selection
            
        Returns:
            Selected path or None if cancelled
        """
        pass
    
    @abstractmethod
    def select_file(self, title: str, initial_dir: Optional[Path] = None, 
                    extensions: Optional[List[str]] = None) -> Optional[Path]:
        """
        Prompt user to select a file.
        
        Args:
            title: Title for the selection dialog/prompt
            initial_dir: Starting directory for selection
            extensions: List of allowed extensions (e.g., ['.docx', '.pptx'])
            
        Returns:
            Selected path or None if cancelled
        """
        pass
    
    @abstractmethod
    def select_from_list(self, title: str, items: List[str]) -> Optional[str]:
        """
        Prompt user to select from a list of options.
        
        Args:
            title: Title for the selection
            items: List of items to choose from
            
        Returns:
            Selected item or None if cancelled
        """
        pass
    
    @abstractmethod
    def open_file_external(self, path: Path) -> bool:
        """
        Open a file with the default system application.
        
        Args:
            path: Path to the file to open
            
        Returns:
            True if opened successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def open_folder(self, path: Path) -> bool:
        """
        Open a folder in the system file explorer.
        
        Args:
            path: Path to the folder to open
            
        Returns:
            True if opened successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def confirm(self, message: str) -> bool:
        """
        Ask user for yes/no confirmation.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if user confirmed, False otherwise
        """
        pass


class TUIProvider(UIProvider):
    """
    Terminal User Interface implementation.
    
    Uses text input and numbered lists for all interactions.
    Suitable for headless environments, SSH sessions, or user preference.
    """
    
    def __init__(self, max_items_display: int = 20):
        self.max_items_display = max_items_display
    
    def select_directory(self, title: str, initial_dir: Optional[Path] = None) -> Optional[Path]:
        """Select directory via terminal navigation."""
        print(f"\n📁 {title}")
        
        current_dir = initial_dir or Path.cwd()
        
        while True:
            print(f"\nDiretório atual: {current_dir}")
            
            # List subdirectories
            try:
                subdirs = sorted([d for d in current_dir.iterdir() if d.is_dir()])
            except PermissionError:
                print("❌ Sem permissão para acessar este diretório.")
                return None
            
            # Show navigation options
            print("\n0. [Selecionar este diretório]")
            print(".. Voltar (diretório pai)")
            
            # Show subdirectories
            for i, d in enumerate(subdirs[:self.max_items_display], 1):
                print(f"{i}. 📁 {d.name}")
            
            if len(subdirs) > self.max_items_display:
                print(f"   ... e mais {len(subdirs) - self.max_items_display} diretórios")
            
            print("q. Cancelar")
            
            choice = input("\nEscolha: ").strip()
            
            if choice == 'q':
                return None
            elif choice == '0':
                return current_dir
            elif choice == '..':
                current_dir = current_dir.parent
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(subdirs):
                    current_dir = subdirs[idx]
                else:
                    print("Opção inválida.")
            else:
                # Try as direct path
                test_path = Path(choice)
                if test_path.is_dir():
                    current_dir = test_path
                else:
                    print("Caminho inválido.")
    
    def select_file(self, title: str, initial_dir: Optional[Path] = None,
                    extensions: Optional[List[str]] = None) -> Optional[Path]:
        """Select file via terminal listing."""
        print(f"\n📄 {title}")
        
        current_dir = initial_dir or Path.cwd()
        
        while True:
            print(f"\nDiretório: {current_dir}")
            
            try:
                # Get files and directories
                entries = sorted(current_dir.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            except PermissionError:
                print("❌ Sem permissão.")
                return None
            
            # Filter files by extension if specified
            if extensions:
                entries = [e for e in entries if e.is_dir() or e.suffix.lower() in extensions]
            
            # Show entries
            print("\n.. Voltar (diretório pai)")
            
            for i, entry in enumerate(entries[:self.max_items_display], 1):
                icon = "📁" if entry.is_dir() else "📄"
                print(f"{i}. {icon} {entry.name}")
            
            if len(entries) > self.max_items_display:
                print(f"   ... e mais {len(entries) - self.max_items_display} itens")
            
            print("q. Cancelar")
            
            choice = input("\nEscolha: ").strip()
            
            if choice == 'q':
                return None
            elif choice == '..':
                current_dir = current_dir.parent
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(entries):
                    selected = entries[idx]
                    if selected.is_dir():
                        current_dir = selected
                    else:
                        return selected
                else:
                    print("Opção inválida.")
            else:
                # Try as direct path
                test_path = Path(choice)
                if test_path.is_file():
                    return test_path
                elif test_path.is_dir():
                    current_dir = test_path
                else:
                    print("Caminho inválido.")
    
    def select_from_list(self, title: str, items: List[str]) -> Optional[str]:
        """Select from numbered list."""
        if not items:
            print("❌ Nenhum item disponível.")
            return None
        
        print(f"\n{title}")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")
        print("0. Cancelar")
        
        try:
            choice = int(input("\nEscolha: ").strip())
            if choice == 0:
                return None
            if 1 <= choice <= len(items):
                return items[choice - 1]
        except ValueError:
            pass
        
        print("Opção inválida.")
        return None
    
    def open_file_external(self, path: Path) -> bool:
        """Open file - in TUI mode, just print the path."""
        print(f"\n📄 Arquivo: {path}")
        print("(Em modo terminal, abra manualmente o arquivo acima)")
        return True
    
    def open_folder(self, path: Path) -> bool:
        """Open folder - in TUI mode, just print the path."""
        print(f"\n📁 Pasta: {path}")
        print("(Em modo terminal, navegue manualmente até a pasta acima)")
        return True
    
    def confirm(self, message: str) -> bool:
        """Simple yes/no confirmation."""
        response = input(f"\n{message} (S/N): ").strip().upper()
        return response == 'S'


class GUIProvider(UIProvider):
    """
    Graphical User Interface implementation using Tkinter.
    
    Uses native file dialogs for better user experience.
    Requires display/windowing system.
    """
    
    def __init__(self):
        self._tk_available = None
    
    def _ensure_tk(self):
        """Lazy-load tkinter and check availability."""
        if self._tk_available is None:
            try:
                import tkinter as tk
                self._tk = tk
                self._tk_available = True
            except ImportError:
                self._tk_available = False
        return self._tk_available
    
    def _create_hidden_root(self):
        """Create a hidden Tk root window for dialogs."""
        root = self._tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        return root
    
    def select_directory(self, title: str, initial_dir: Optional[Path] = None) -> Optional[Path]:
        """Select directory via native dialog."""
        if not self._ensure_tk():
            # Fallback to TUI
            return TUIProvider().select_directory(title, initial_dir)
        
        from tkinter import filedialog
        
        root = self._create_hidden_root()
        try:
            path = filedialog.askdirectory(
                title=title,
                initialdir=str(initial_dir) if initial_dir else None
            )
            return Path(path) if path else None
        finally:
            root.destroy()
    
    def select_file(self, title: str, initial_dir: Optional[Path] = None,
                    extensions: Optional[List[str]] = None) -> Optional[Path]:
        """Select file via native dialog."""
        if not self._ensure_tk():
            return TUIProvider().select_file(title, initial_dir, extensions)
        
        from tkinter import filedialog
        
        root = self._create_hidden_root()
        try:
            filetypes = [("Todos os arquivos", "*.*")]
            if extensions:
                ext_str = " ".join(f"*{ext}" for ext in extensions)
                filetypes.insert(0, ("Arquivos permitidos", ext_str))
            
            path = filedialog.askopenfilename(
                title=title,
                initialdir=str(initial_dir) if initial_dir else None,
                filetypes=filetypes
            )
            return Path(path) if path else None
        finally:
            root.destroy()
    
    def select_from_list(self, title: str, items: List[str]) -> Optional[str]:
        """For list selection, fall back to TUI (no native dialog)."""
        return TUIProvider().select_from_list(title, items)
    
    def open_file_external(self, path: Path) -> bool:
        """Open file with default system application."""
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                import subprocess
                subprocess.run(['xdg-open', str(path)], check=True)
            return True
        except Exception:
            return False
    
    def open_folder(self, path: Path) -> bool:
        """Open folder in system file explorer."""
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                import subprocess
                subprocess.run(['xdg-open', str(path)], check=True)
            return True
        except Exception:
            return False
    
    def confirm(self, message: str) -> bool:
        """For simple confirmation, use TUI (cleaner UX)."""
        return TUIProvider().confirm(message)


def get_ui_provider(mode: str = 'auto') -> UIProvider:
    """
    Factory function to get the appropriate UI provider.
    
    Args:
        mode: 'tui', 'gui', or 'auto' (detect best option)
        
    Returns:
        UIProvider instance
    """
    if mode == 'tui':
        return TUIProvider()
    elif mode == 'gui':
        return GUIProvider()
    else:
        # Auto-detect: use GUI if display is available
        if os.name == 'nt':
            # Windows usually has GUI
            return GUIProvider()
        elif os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
            # Linux/Mac with display
            return GUIProvider()
        else:
            # No display, use TUI
            return TUIProvider()
