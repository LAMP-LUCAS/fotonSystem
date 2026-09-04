import os
import sys
import shutil
import time
import subprocess
from pathlib import Path
from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.shared.infrastructure.services.environment_porter import get_porter

logger = setup_logger()


class InstallService:
    def __init__(self):
        self.app_name = "FotonSystem"
        self.porter = get_porter()
        if self.porter.os_type == 'windows':
             self.install_dir = Path(os.environ.get('LOCALAPPDATA', '')) / self.app_name
        else:
             self.install_dir = Path.home() / ".local" / "share" / self.app_name.lower()
        self.bin_dir = self.install_dir / "bin"

    def _exe_name_pattern(self):
        return "foton_system_v*"

    # ------------------------------------------------------------------
    # Template: Windows (.bat)
    # ------------------------------------------------------------------
    def _deploy_bat(self, source_internal, target_internal, old_internal, target_exe):
        bat_path = Path(os.environ.get('TEMP', '')) / f"foton_delayed_{int(time.time())}.bat"
        first_run_marker = target_internal.parent / '.first_run'
        exe_name = self._exe_name_pattern()
        lines = [
            "@echo off",
            "title FotonSystem - Concluindo Instala\u00e7\u00e3o",
            "chcp 65001 >nul 2>&1",
            "",
            f'set "SRC={source_internal}"',
            f'set "DST={target_internal}"',
            f'set "OLD={old_internal}"' if old_internal else 'set "OLD="',
            f'set "EXE={target_exe}"',
            f'set "MARKER={first_run_marker}"',
            f'set "EXE_MATCH={exe_name}"',
            "",
            "echo Fechando instancias do FotonSystem...",
            'taskkill /f /im "%EXE_MATCH%" >nul 2>&1',
            "timeout /t 3 /nobreak >nul",
            "",
            "echo Copiando dependencias...",
            'if exist "%DST%" rmdir /s /q "%DST%" >nul 2>&1',
            'if defined OLD if exist "%OLD%" rmdir /s /q "%OLD%" >nul 2>&1',
            'if exist "%SRC%" (',
            '    xcopy "%SRC%" "%DST%" /E /I /Q /Y >nul 2>&1',
            ')',
            "",
            "echo 1 > \"%MARKER%\"",
            "",
            'start "" "%EXE%"',
            "",
            "del /f /q \"%~f0\" >nul 2>&1",
        ]
        bat_path.write_text('\r\n'.join(lines), encoding='utf-8')
        subprocess.Popen(
            ['cmd', '/c', 'start', '/min', '', str(bat_path)],
            shell=True, close_fds=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return bat_path

    # ------------------------------------------------------------------
    # Template: Unix (.sh)
    # ------------------------------------------------------------------
    def _deploy_sh(self, source_internal, target_internal, old_internal, target_exe):
        sh_path = Path(tempfile.gettempdir()) / f"foton_delayed_{int(time.time())}.sh"
        first_run_marker = target_internal.parent / '.first_run'
        exe_name = self._exe_name_pattern()
        lines = [
            "#!/bin/sh",
            "echo 'FotonSystem - Concluindo Instala\u00e7\u00e3o'",
            "",
            f'SRC="{source_internal}"',
            f'DST="{target_internal}"',
            f'OLD="{old_internal}"',
            f'EXE="{target_exe}"',
            f'EXE_MATCH="{exe_name}"',
            f'MARKER="{first_run_marker}"',
            "",
            'echo "Fechando instancias do FotonSystem..."',
            'pkill -f "$EXE_MATCH" 2>/dev/null',
            'sleep 3',
            "",
            'echo "Copiando dependencias..."',
            'rm -rf "$DST" 2>/dev/null',
            '[ -n "$OLD" ] && rm -rf "$OLD" 2>/dev/null',
            '[ -d "$SRC" ] && cp -r "$SRC" "$DST" 2>/dev/null',
            "",
            'echo "1" > "$MARKER"',
            "",
            'nohup "$EXE" >/dev/null 2>&1 &',
            "",
            'rm -f "$0"',
        ]
        sh_path.write_text('\n'.join(lines), encoding='utf-8')
        os.chmod(sh_path, 0o755)
        subprocess.Popen(
            ['sh', str(sh_path)],
            close_fds=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return sh_path

    # ------------------------------------------------------------------
    # Main install
    # ------------------------------------------------------------------
    def install(self):
        """Realiza a instala\u00e7\u00e3o completa no sistema.

        Returns:
            None on success (inline copy worked).
            "KILL_SWITCH" when deferred script was deployed.
        """
        print(f"Instalando {self.app_name} em {self.install_dir}...")
        self.bin_dir.mkdir(parents=True, exist_ok=True)

        exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
        exe_path = Path(exe_path).resolve()
        source_dir = exe_path.parent
        target_exe = self.bin_dir / exe_path.name

        if exe_path.resolve() == target_exe.resolve():
            logger.info("Execut\u00e1vel j\u00e1 est\u00e1 no destino de instala\u00e7\u00e3o. Pulando c\u00f3pia.")
            print("O sistema j\u00e1 est\u00e1 rodando a partir da pasta de instala\u00e7\u00e3o.")
            return None

        print(f"Preparando bin\u00e1rios em: {self.bin_dir}")
        try:
            if target_exe.exists():
                try:
                    timestamp = int(time.time())
                    temp_old = target_exe.with_suffix(f".old_{timestamp}")
                    target_exe.rename(temp_old)
                except Exception as e:
                    logger.debug(f"N\u00e3o foi poss\u00edvel renomear exe antigo: {e}")

            shutil.copy2(exe_path, target_exe)
            print(f"Execut\u00e1vel copiado.")

            source_internal = source_dir / "_internal"
            target_internal = self.bin_dir / "_internal"

            if source_internal.exists():
                print(f"Atualizando depend\u00eancias (_internal)...")

                old_internal = None
                if target_internal.exists():
                    try:
                        timestamp = int(time.time())
                        old_internal = target_internal.parent / f"_internal_old_{timestamp}"
                        target_internal.rename(old_internal)
                    except (IOError, OSError):
                        pass

                # Try direct copy (works in Python source / non-frozen mode)
                print(f"   Tentando c\u00f3pia direta...")
                direct_ok = True
                for src_file in source_internal.rglob('*'):
                    if not src_file.is_file():
                        continue
                    rel_path = src_file.relative_to(source_internal)
                    dst_file = target_internal / rel_path
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.copy2(src_file, dst_file)
                    except (PermissionError, OSError):
                        direct_ok = False
                        break

                if direct_ok:
                    print(f"Depend\u00eancias atualizadas.")
                    if old_internal and old_internal.exists():
                        shutil.rmtree(old_internal, ignore_errors=True)
                    self._finalize_install(target_exe)
                    return None

                # Deferred copy via native shell script
                print(f"   DLLs bloqueadas pelo processo em execu\u00e7\u00e3o...")
                platform = sys.platform
                if platform == 'win32':
                    self._deploy_bat(source_internal, target_internal, old_internal, target_exe)
                else:
                    import tempfile
                    self._deploy_sh(source_internal, target_internal, old_internal, target_exe)
                return "KILL_SWITCH"

        except Exception as e:
            logger.error(f"Erro ao copiar arquivos: {e}")
            print(f"Erro ao instalar bin\u00e1rios: {e}")
            return None

        self._finalize_install(target_exe)
        return None

    def _finalize_install(self, target_exe):
        """Cria configura\u00e7\u00e3o e atalhos (etapas p\u00f3s-c\u00f3pia de arquivos)."""
        config_path = BootstrapService.initialize()
        print(f"Configura\u00e7\u00e3o vinculada em: {config_path}")

        integrator = self.porter.get_integrator()
        success = integrator.create_shortcut(
            target_exe,
            self.app_name,
            "Sistema de Gest\u00e3o para Arquitetos"
        )
        if success:
            print(f"Atalhos de sistema criados com sucesso!")
        else:
            print(f"N\u00e3o foi poss\u00edvel criar atalhos autom\u00e1ticos para este ambiente.")

        print(f"\n{self.app_name} instalado com sucesso!")
