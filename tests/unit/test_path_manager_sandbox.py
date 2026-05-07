import unittest
import os
from pathlib import Path
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager

class TestPathManagerSandbox(unittest.TestCase):
    """
    TDD for Sandbox Mode Redirection in PathManager.
    """

    def setUp(self):
        # Reset state before each test
        PathManager.set_sandbox_mode(False)

    def test_default_mode_returns_standard_paths(self):
        """Standard paths should be returned when sandbox is OFF."""
        app_data = PathManager.get_app_data_dir()
        if os.name == 'nt':
            self.assertIn("AppData", str(app_data))
        else:
            self.assertTrue(str(app_data).startswith(str(Path.home())))

    def test_sandbox_mode_redirects_paths(self):
        """Paths should be redirected to a temporary directory when sandbox is ON."""
        PathManager.set_sandbox_mode(True)
        
        sandbox_dir = PathManager.get_sandbox_dir()
        app_data = PathManager.get_app_data_dir()
        projects = PathManager.get_user_projects_dir()
        
        self.assertTrue(str(app_data).startswith(str(sandbox_dir)))
        self.assertTrue(str(projects).startswith(str(sandbox_dir)))
        self.assertIn("foton_sandbox", str(sandbox_dir))

    def test_sandbox_dir_is_volatile(self):
        """The sandbox directory should be inside the system temp folder."""
        PathManager.set_sandbox_mode(True)
        sandbox_dir = PathManager.get_sandbox_dir()
        
        import tempfile
        sys_temp = Path(tempfile.gettempdir())
        
        self.assertTrue(str(sandbox_dir).startswith(str(sys_temp)))

    def test_switching_off_restores_paths(self):
        """Paths should return to normal after turning off sandbox."""
        PathManager.set_sandbox_mode(True)
        PathManager.set_sandbox_mode(False)
        
        app_data = PathManager.get_app_data_dir()
        if os.name == 'nt':
            self.assertIn("AppData", str(app_data))
        else:
            self.assertNotIn("foton_sandbox", str(app_data))

if __name__ == '__main__':
    unittest.main()
