import unittest
import os
import shutil
import tempfile
import time
import threading
from pathlib import Path
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.domain.exceptions import DatabaseLockError

class TestIOResilience(unittest.TestCase):
    """
    Tests the system's resilience to file locks (OneDrive/Excel open).
    """

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.gettempdir()) / "foton_io_test"
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir)
        cls.temp_dir.mkdir(parents=True)

        PathManager._sandbox_dir = cls.temp_dir
        PathManager.set_sandbox_mode(True)
        PathManager.ensure_directories()

        config = Config()
        config.set('caminho_baseDados', str(PathManager.get_app_data_dir() / "baseDados_io.xlsx"))
        config.save()

        cls.repo = ExcelClientRepository()

    def test_excel_lock_retry_mechanism(self):
        """
        Simulates an Excel file lock and verifies the retry with backoff.
        """
        df = self.repo.get_clients_dataframe()
        db_path = PathManager.get_app_data_dir() / "baseDados_io.xlsx"

        # 1. Make file read-only to trigger PermissionError
        import stat
        os.chmod(db_path, stat.S_IREAD) # Set Read-Only
        
        # 2. Try to save while locked in a separate thread so we can release it
        results = {"success": False, "duration": 0, "error": None}
        
        def attempt_save():
            start_time = time.time()
            try:
                self.repo.save_clients(df)
                results["duration"] = time.time() - start_time
                results["success"] = True
            except Exception as e:
                results["error"] = e

        save_thread = threading.Thread(target=attempt_save)
        save_thread.start()

        # Wait a bit, then restore write permission
        # The backoff is: 0.5, 1.0, 2.0
        # By waiting 0.7s, the first retry (at 0.5s) might still fail, 
        # but the second one (at 0.5 + 1.0 = 1.5s) should succeed.
        time.sleep(0.7)
        os.chmod(db_path, stat.S_IWRITE) # Restore Write
        
        save_thread.join()

        # 3. Validations
        if results["error"]:
            self.fail(f"O sistema falhou com erro: {results['error']}")
            
        self.assertTrue(results["success"], "O sistema falhou em salvar o arquivo após a liberação do lock.")
        self.assertGreater(results["duration"], 1.5, f"Deveria ter esperado pelo menos uma tentativa de retry. Durou {results['duration']:.2f}s")
        print(f"\n✅ Retry bem-sucedido após {results['duration']:.2f}s")

    @classmethod
    def tearDownClass(cls):
        PathManager.set_sandbox_mode(False)
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir)

if __name__ == '__main__':
    unittest.main()
