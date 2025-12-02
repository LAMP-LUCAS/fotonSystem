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
    if dist_dir.exists(): shutil.rmtree(dist_dir)
    if build_dir.exists(): shutil.rmtree(build_dir)
    
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
        '--clean',
        '--noconfirm',
        # Add assets (source:dest)
        f'--add-data={base_dir / "foton_system" / "assets"}{os.pathsep}foton_system/assets',
        # Hidden imports often needed for pandas/openpyxl
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=docx',
        '--hidden-import=pptx',
        '--hidden-import=plyer.platforms.win.notification',
        '--hidden-import=requests',
    ]
    
    PyInstaller.__main__.run(args)
    
    print("\nBuild complete!")
    print(f"Executable located at: {dist_dir / f'{exe_name}.exe'}")

if __name__ == "__main__":
    build()
