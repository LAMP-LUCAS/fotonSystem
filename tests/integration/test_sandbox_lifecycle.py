import unittest
import shutil
from pathlib import Path
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
from foton_system.modules.shared.infrastructure.services.sandbox_service import SandboxService

class TestSandboxLifecycle(unittest.TestCase):
    """
    Integration test for the Sandbox lifecycle:
    Initialize -> Seed -> Verify -> Cleanup.
    """

    def setUp(self):
        PathManager.set_sandbox_mode(False)

    def test_sandbox_initialization_creates_folders(self):
        """SandboxService should create the directory structure."""
        SandboxService.initialize_sandbox()
        
        self.assertTrue(PathManager.is_sandbox_active())
        self.assertTrue(PathManager.get_app_data_dir().exists())
        self.assertTrue(PathManager.get_user_projects_dir().exists())
        
        # Verify settings.json was created in sandbox
        settings_path = PathManager.get_settings_path()
        self.assertTrue(settings_path.exists())

    def test_sandbox_seeding(self):
        """Sandbox should be seeded with dummy data."""
        SandboxService.initialize_sandbox()
        
        # Check for dummy client or template
        clients_dir = PathManager.get_user_projects_dir()
        dummy_client = clients_dir / "CLIENTE_EXEMPLO"
        self.assertTrue(dummy_client.exists())
        
        # Check for dummy template
        # (Assuming we define what resources are copied)
        templates_dir = PathManager.get_sandbox_dir() / "templates"
        self.assertTrue(templates_dir.exists())

    def tearDown(self):
        # Clean up sandbox
        if PathManager.is_sandbox_active():
            sandbox_dir = PathManager.get_sandbox_dir()
            PathManager.set_sandbox_mode(False)
            if sandbox_dir.exists():
                shutil.rmtree(sandbox_dir, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
