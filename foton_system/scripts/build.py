"""
FotonSystem Build Script

Generates a distributable package using PyInstaller with the hybrid onedir strategy.
Optimized for fast builds and instant startup.
"""

import PyInstaller.__main__
import os
import sys
import time
import shutil
import subprocess
import argparse
from pathlib import Path


def robust_rmtree(path: Path, max_retries: int = 3) -> bool:
    """
    Robustly removes a directory tree, handling OneDrive and antivirus locks.
    
    Args:
        path: Path to remove
        max_retries: Number of retry attempts
    
    Returns:
        True if successful, False otherwise
    """
    if not path.exists():
        return True
    
    for attempt in range(max_retries):
        try:
            shutil.rmtree(path)
            return True
        except PermissionError as e:
            if attempt < max_retries - 1:
                print(f"⏳ Folder locked, retrying in 2s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
            else:
                # Try using Windows rmdir as fallback
                try:
                    subprocess.run(
                        ['cmd', '/c', 'rmdir', '/s', '/q', str(path)],
                        check=True,
                        capture_output=True
                    )
                    return True
                except subprocess.CalledProcessError:
                    print(f"⚠️ Could not remove {path.name}: {e}")
                    print(f"   Please close any programs using these files and try again.")
                    print(f"   Or manually delete: {path}")
                    return False
        except Exception as e:
            print(f"⚠️ Error removing {path.name}: {e}")
            return False
    
    return False


def build():
    """Main build function."""
    parser = argparse.ArgumentParser(description="FotonSystem Build Script")
    parser.add_argument("--clean", action="store_true", help="Clear PyInstaller cache before building")
    parser.add_argument("--type", choices=["lite", "full"], default="lite", help="Build type: lite (small, excludes AI) or full (includes everything)")
    cli_args = parser.parse_args()
    
    # Base paths
    base_dir = Path(__file__).resolve().parent.parent.parent
    main_script = base_dir / "foton_system" / "main.py"
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    
    print("=" * 60)
    print("  🚀 FotonSystem Build Script")
    print("=" * 60)
    if cli_args.clean:
        print(f"{'MODO LIMPEZA ATIVADO':^60}")
    print("")
    
    # Clean previous builds with robust deletion
    print("🧹 Cleaning previous builds...")
    dist_cleaned = robust_rmtree(dist_dir)
    build_cleaned = robust_rmtree(build_dir)
    
    if not dist_cleaned or not build_cleaned:
        print("")
        print("❌ Build aborted due to locked files.")
        print("   Suggestions:")
        print("   1. Close any running FotonSystem instances")
        print("   2. Pause OneDrive sync (right-click icon > Pause)")
        print("   3. Temporarily disable antivirus real-time scanning")
        print("   4. Manually delete 'build/' and 'dist/' folders")
        sys.exit(1)
    
    # Get version from __init__.py
    init_file = base_dir / "foton_system" / "__init__.py"
    version = "0.0.0"
    try:
        with open(init_file, "r", encoding="utf-8") as f:
            for line in f:
                if "__version__" in line:
                    version = line.split("=")[1].strip().strip('"').strip("'")
                    break
    except Exception as e:
        print(f"⚠️ Could not read version: {e}")
    
    exe_name = f"foton_system_v{version}"
    icon_path = base_dir / "foton_system" / "assets" / "foton.ico"
    
    # Write version.txt for Inno Setup dynamic version
    version_file = base_dir / "version.txt"
    version_file.write_text(version, encoding='utf-8')
    
    print(f"📦 Building version: {version}")
    print(f"📄 Entry point: {main_script}")
    print(f"🎨 Icon: {icon_path}")
    print("")
    
    # PyInstaller arguments
    args = [
        str(main_script),
        f'--name={exe_name}',
        '--onedir',                            # Hybrid: Faster startup and easier debugging
        '--noconfirm',                         # Override existing dist/build
        '--noupx',                             # DISABLE UPX: Faster build and faster startup
        
        # Paths
        f'--distpath={dist_dir}',
        f'--workpath={build_dir}',
        f'--specpath={base_dir}',
        
        # Icon
        f'--icon={icon_path}',
        
        # Add assets (source:dest)
        f'--add-data={base_dir / "foton_system" / "assets"}{os.pathsep}foton_system/assets',
        f'--add-data={base_dir / "foton_system" / "config"}{os.pathsep}foton_system/config',
        f'--add-data={base_dir / "foton_system" / "scripts"}{os.pathsep}foton_system/scripts',
        f'--add-data={base_dir / "foton_system" / "resources"}{os.pathsep}foton_system/resources',
        f'--add-data={base_dir / "foton_system" / "interfaces"}{os.pathsep}foton_system/interfaces',
        
        # Robustness Flags
        '--collect-all=plyer',
        '--collect-all=colorama',
        '--collect-all=watchdog',
        '--collect-all=setuptools',
        '--collect-all=pywebview',
    ]

    # Exclusions for LITE build
    if cli_args.type == "lite":
        print("💡 Building LITE version (AI modules will be installed on-demand)")
        args.extend([
            '--exclude-module=matplotlib',
            '--exclude-module=PyQt6',
            '--exclude-module=PySide6',
            '--exclude-module=tensorflow',
            '--exclude-module=notebook',
            '--exclude-module=scipy',
            '--exclude-module=sklearn',
            '--exclude-module=pygame',
            '--exclude-module=torch.distributed',
            '--exclude-module=torch.utils.tensorboard',
            '--exclude-module=altair',
            '--exclude-module=IPython',
            '--exclude-module=ipykernel',
            '--exclude-module=nbformat',
            '--exclude-module=nbconvert',
            '--exclude-module=uvicorn',
            '--exclude-module=websockets',
            '--exclude-module=chromadb',
            '--exclude-module=sentence_transformers',
            '--exclude-module=torch',
            '--exclude-module=transformers',
        ])
    else:
        print("🔥 Building FULL version (Includes all AI modules)")

    # Core dependencies
    args.extend([
        '--hidden-import=pandas',
        '--hidden-import=pandas.plotting',
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
        '--hidden-import=foton_system.core.ops',
        '--hidden-import=colorama',
        '--hidden-import=plyer',
        '--hidden-import=watchdog.observers',
        '--hidden-import=watchdog.events',
        '--hidden-import=webview',
        '--hidden-import=jaraco',
        '--hidden-import=json',
    ])

    # RAG dependencies (Only for FULL build)
    if cli_args.type == "full":
        print("🧠 Adding AI dependencies to bundle...")
        args.extend([
            '--hidden-import=chromadb',
            '--hidden-import=chromadb.config',
            '--hidden-import=chromadb.api',
            '--hidden-import=chromadb.api.models',
            '--hidden-import=sentence_transformers',
            '--hidden-import=torch',
            '--hidden-import=transformers',
            '--hidden-import=tokenizers',
            '--hidden-import=tqdm',
            '--hidden-import=huggingface_hub',
            '--hidden-import=foton_system.core.ops.op_query_knowledge',
            '--hidden-import=foton_system.core.ops.op_index_knowledge',
            '--hidden-import=foton_system.core.memory',
            '--hidden-import=foton_system.core.memory.vector_store',
        ])
    else:
        # For LITE build, we still need these to be discoverable but not necessarily bundled
        # unless they are already in the environment. However, since we use DependencyManager
        # to load them from a VENV, we should NOT bundle them here.
        pass

    # Conditional Clean
    if cli_args.clean:
        args.append('--clean')
    
    # Run PyInstaller
    print("⚙️ Running PyInstaller...")
    print("-" * 60)
    
    try:
        PyInstaller.__main__.run(args)
    except SystemExit as e:
        if e.code != 0:
            print(f"\n❌ PyInstaller failed with exit code {e.code}")
            sys.exit(e.code)
    
    print("-" * 60)
    
    # Post-build: Zip the result
    output_folder = dist_dir / exe_name
    zip_path = dist_dir / f"{exe_name}.zip"
    
    if output_folder.exists():
        print(f"\n📦 Creating ZIP archive...")
        try:
            shutil.make_archive(str(dist_dir / exe_name), 'zip', output_folder)
            print(f"   ✅ Created: {zip_path}")
        except Exception as e:
            print(f"   ⚠️ Could not create ZIP: {e}")
        
        print("")
        print("=" * 60)
        print("  ✅ BUILD COMPLETE!")
        print("=" * 60)
        print(f"  📁 Folder: {output_folder}")
        print(f"  📦 ZIP:    {zip_path}")
        print("")
        print("  Next steps:")
        print("  1. Test the EXE in the dist folder")
        print("  2. Compile installer/foton_setup.iss with Inno Setup")
        print("")
    else:
        print("\n❌ Build failed: output folder not found")
        sys.exit(1)


if __name__ == "__main__":
    build()
