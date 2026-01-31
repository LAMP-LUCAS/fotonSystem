import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build():
    # Base paths
    base_dir = Path(__file__).resolve().parent.parent.parent
    main_script = base_dir / "foton_system" / "main.py"
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    
    # Clean previous builds
    if dist_dir.exists():
        try:
            shutil.rmtree(dist_dir)
        except Exception as e:
            print(f"Warning: Could not remove dist dir: {e}")
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
        except Exception as e:
            print(f"Warning: Could not remove build dir: {e}")
    
    # Get version
    init_file = base_dir / "foton_system" / "__init__.py"
    version = "0.0.0"
    with open(init_file, "r") as f:
        for line in f:
            if "__version__" in line:
                version = line.split("=")[1].strip().strip('"').strip("'")
                break
    
    exe_name = f"foton_system_v{version}"
    print(f"Building version: {version}")
    print(f"Building from: {main_script}")
    
    # PyInstaller arguments
    args = [
        str(main_script),
        f'--name={exe_name}',
        '--onefile',
        # '--clean',
        '--noconfirm',
        # Add assets (source:dest)
        f'--add-data={base_dir / "foton_system" / "assets"}{os.pathsep}foton_system/assets',
        f'--add-data={base_dir / "foton_system" / "config"}{os.pathsep}foton_system/config',
        f'--add-data={base_dir / "foton_system" / "scripts"}{os.pathsep}foton_system/scripts',
        f'--add-data={base_dir / "foton_system" / "resources"}{os.pathsep}foton_system/resources',
        # Hidden imports often needed for pandas/openpyxl
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=docx',
        '--hidden-import=pptx',
        '--hidden-import=plyer.platforms.win.notification',
        '--hidden-import=requests',
        '--hidden-import=tkinter',
        '--hidden-import=mcp',
        '--hidden-import=winshell',
        '--hidden-import=win32com',
        '--hidden-import=pythoncom',
        '--hidden-import=foton_system.modules.finance',
        '--hidden-import=foton_system.modules.sync',
        '--hidden-import=colorama',
        '--hidden-import=plyer',
    ]
    
    PyInstaller.__main__.run(args)
    
    print("\nBuild complete!")
    print(f"Executable located at: {dist_dir / f'{exe_name}.exe'}")

if __name__ == "__main__":
    build()
