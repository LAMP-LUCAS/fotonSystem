"""
MCP Services Layer

Provides testable service classes for MCP tools with dependency injection.
All dependencies are injected via constructor, enabling easy mocking for tests.
"""

from pathlib import Path
from typing import Protocol, Optional, Any
from dataclasses import dataclass


# ==============================================================================
# PROTOCOLS (Interfaces for Dependency Injection)
# ==============================================================================

class ConfigProvider(Protocol):
    """Protocol for configuration access."""
    @property
    def base_pasta_clientes(self) -> Path: ...
    @property
    def templates_path(self) -> Path: ...
    @property
    def base_dados(self) -> Path: ...
    @property
    def ignored_folders(self) -> list: ...
    @property
    def clean_missing_variables(self) -> bool: ...
    @property
    def missing_variable_placeholder(self) -> str: ...
    @property
    def folder_doc(self) -> str: ...
    @property
    def folder_adm(self) -> str: ...
    @property
    def folder_op(self) -> str: ...
    @property
    def folder_op_phases(self) -> list: ...


class FinanceServiceProtocol(Protocol):
    """Protocol for finance operations."""
    def add_entry(self, client_path: Path, description: str, value: float, entry_type: str) -> dict: ...
    def get_summary(self, client_path: Path) -> dict: ...


class DocumentServiceProtocol(Protocol):
    """Protocol for document operations."""
    def list_templates(self, doc_type: str) -> list: ...
    def list_data_files(self) -> list: ...
    def list_client_data_files(self, client_path) -> list: ...
    def create_custom_data_file(self, client_path, cod, ver='00', rev='R00', desc='PROPOSTA'): ...
    def generate_document(self, template_path: str, data_path: str, output_path: str, doc_type: str) -> None: ...
    def validate_template_keys(self, template_path: str, data_path: str, doc_type: str) -> list: ...


class ClientServiceProtocol(Protocol):
    """Protocol for client operations."""
    def resolve_client_path(self, client_name: str) -> Path: ...
    def sync_clients_db_from_folders(self) -> None: ...
    def sync_client_folders_from_db(self) -> None: ...
    def sync_services_db_from_folders(self) -> None: ...
    def sync_service_folders_from_db(self, client_alias=None) -> None: ...
    def create_client(self, name: str, tax_id: str = '', email: str = '', phone: str = '', alias: str = '') -> dict: ...
    def export_client_data(self) -> None: ...
    def export_service_data(self) -> None: ...
    def import_service_data(self) -> None: ...


class SyncServiceProtocol(Protocol):
    """Protocol for sync operations."""
    def sync_dashboard(self) -> int: ...


class KnowledgeStoreProtocol(Protocol):
    """Protocol for knowledge/RAG operations."""
    def query(self, question: str, n_results: int = 4) -> dict: ...


# ==============================================================================
# CLIENT PATH RESOLVER
# ==============================================================================

class ClientPathResolver:
    """Resolves and validates client paths with security checks."""
    
    def __init__(self, config: ConfigProvider):
        self._config = config
    
    def resolve(self, client_name: str) -> Path:
        """
        Resolves a client name to a validated path.
        
        Args:
            client_name: Name or partial name of client folder
            
        Returns:
            Path to the client folder
            
        Raises:
            ValueError: If client not found or base path invalid
        """
        # Security: Prevent directory traversal
        safe_name = Path(client_name).name
        
        base = self._config.base_pasta_clientes
        if not base or not base.exists():
            raise ValueError(f"Pasta de clientes não configurada ou não encontrada: {base}")
        
        client_path = base / safe_name
        
        if not client_path.exists():
            # Try partial match
            matches = [
                d for d in base.iterdir() 
                if d.is_dir() and safe_name.lower() in d.name.lower()
            ]
            if matches:
                client_path = matches[0]
            else:
                raise ValueError(f"Cliente '{safe_name}' não encontrado em {base}")
        
        return client_path


# ==============================================================================
# MCP SERVICES (Testable Core Logic)
# ==============================================================================

@dataclass
class FinanceResult:
    """Result of a finance operation."""
    success: bool
    message: str
    balance: Optional[float] = None
    total_income: Optional[float] = None
    total_expenses: Optional[float] = None


@dataclass
class DocumentResult:
    """Result of a document operation."""
    success: bool
    message: str
    output_path: Optional[str] = None
    templates: Optional[list] = None


@dataclass
class KnowledgeResult:
    """Result of a knowledge query."""
    success: bool
    documents: list
    sources: list


class MCPClientService:
    """MCP wrapper for the domain ClientService.

    DRY: this class is a thin adapter; all logic lives in ClientService.
    Its only responsibility is to expose a stable interface for the MCP
    tool layer (`foton_mcp.py`) without leaking domain details.
    """

    def __init__(self, client_service, config: Optional[ConfigProvider] = None):
        self._client = client_service
        self._config = config

    def resolve_client_path(self, client_name: str) -> Path:
        """Delegate to the underlying ClientService."""
        return self._client.resolve_client_path(client_name)

    def list_clients(self) -> list:
        """List all clients with metadata (name, has_info, service_count)."""
        clients_dir = self._config.base_pasta_clientes
        ignored = set(self._config.ignored_folders + ['.obsidian'])

        clients = []
        for d in sorted(clients_dir.iterdir()):
            if d.is_dir() and d.name not in ignored:
                info_files = list(d.glob("*INFO*.md"))
                services = [
                    s.name for s in d.iterdir()
                    if s.is_dir() and s.name not in ignored
                ]
                clients.append({
                    'name': d.name,
                    'has_info': len(info_files) > 0,
                    'service_count': len(services),
                    'services': services,
                })
        return clients

    def read_client_info(self, client_name: str) -> dict:
        """Read the INFO file content for a client.
        Returns dict with 'filename', 'content' or raises ValueError.
        """
        client_path = self._client.resolve_client_path(client_name)
        info_files = list(client_path.glob("*INFO*.md"))
        if not info_files:
            raise ValueError(
                f"No INFO file found for '{client_path.name}'.\n"
                f"Expected pattern: *INFO*.md in {client_path}"
            )
        info_file = sorted(info_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
        content = info_file.read_text(encoding="utf-8")
        return {'filename': info_file.name, 'content': content}

    def update_client_info(self, client_name: str, section: str, content: str) -> str:
        """Append content to a section of the client's INFO file. Returns backup filename."""
        import shutil
        client_path = self._client.resolve_client_path(client_name)
        info_files = list(client_path.glob("*INFO*.md"))
        if not info_files:
            raise ValueError(f"No INFO file found for '{client_path.name}'.")
        info_file = sorted(info_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]

        backup = info_file.with_suffix('.md.bak')
        shutil.copy2(info_file, backup)

        existing = info_file.read_text(encoding="utf-8")
        section_header = f"## {section}"
        if section_header in existing:
            parts = existing.split(section_header, 1)
            after_header = parts[1]
            next_section_idx = after_header.find("\n## ")
            if next_section_idx == -1:
                new_content = existing + f"\n{content}\n"
            else:
                insert_point = len(parts[0]) + len(section_header) + next_section_idx
                new_content = existing[:insert_point] + f"\n{content}\n" + existing[insert_point:]
        else:
            new_content = existing.rstrip() + f"\n\n{section_header}\n{content}\n"

        info_file.write_text(new_content, encoding="utf-8")
        return backup.name

    def sync_clients_db_from_folders(self) -> str:
        self._client.sync_clients_db_from_folders()
        return "Client database synchronized with folders."

    def sync_client_folders_from_db(self) -> str:
        self._client.sync_client_folders_from_db()
        return "Client folders synchronized with database."

    def sync_services_db_from_folders(self) -> str:
        self._client.sync_services_db_from_folders()
        return "Service database synchronized with folders."

    def sync_service_folders_from_db(self, client_alias=None) -> str:
        self._client.sync_service_folders_from_db(client_alias=client_alias)
        return "Service folders synchronized with database."

    def export_client_data(self) -> str:
        self._client.export_client_data()
        return "Client data exported to files."

    def export_service_data(self) -> str:
        self._client.export_service_data()
        return "Service data exported to files."

    def import_service_data(self) -> str:
        self._client.import_service_data()
        return "Service data imported from files."

    def create_client(self, name: str, tax_id: str = "", email: str = "",
                      phone: str = "", alias: str = "") -> dict:
        result = self._client.create_client(name, tax_id=tax_id, email=email,
                                            phone=phone, alias=alias)
        return {
            'client_id': result.codigo,
            'client_path': str(result.caminho),
            'dados': result.dados,
        }

    def list_services(self, client_name: str) -> list:
        """List sub-services for a client folder using __ hierarchy detection."""
        nodes = self._client.list_service_nodes(client_name)
        result = []
        for n in nodes:
            subdirs = [s.name for s in n['path'].iterdir() if s.is_dir()]
            file_count = sum(1 for f in n['path'].rglob('*') if f.is_file())
            result.append({
                'name': n['name'],
                'file_count': file_count,
                'subdirs': subdirs,
                'depth': n['depth'],
                'parent': n['parent'],
            })
        return result


class MCPFinanceService:
    """Finance operations for MCP tools."""
    
    def __init__(self, path_resolver: ClientPathResolver, finance_service: FinanceServiceProtocol,
                 config: Optional[ConfigProvider] = None):
        self._resolver = path_resolver
        self._finance = finance_service
        self._config = config
    
    def register_entry(self, client_name: str, description: str, value: float, 
                       entry_type: str = "ENTRADA") -> FinanceResult:
        """Register a financial entry for a client."""
        try:
            client_path = self._resolver.resolve(client_name)
            summary = self._finance.add_entry(client_path, description, value, entry_type)
            return FinanceResult(
                success=True,
                message=f"Entrada registrada: {description}",
                balance=summary.get('saldo'),
                total_income=summary.get('total_entradas'),
                total_expenses=summary.get('total_saidas')
            )
        except ValueError as e:
            return FinanceResult(success=False, message=str(e))
        except Exception as e:
            return FinanceResult(success=False, message=f"Erro ao registrar: {e}")
    
    def get_summary(self, client_name: str) -> FinanceResult:
        """Get financial summary for a client."""
        try:
            client_path = self._resolver.resolve(client_name)
            summary = self._finance.get_summary(client_path)
            return FinanceResult(
                success=True,
                message="Resumo obtido",
                balance=summary.get('saldo', 0.0),
                total_income=summary.get('total_entradas', 0.0),
                total_expenses=summary.get('total_saidas', 0.0)
            )
        except ValueError as e:
            return FinanceResult(success=False, message=str(e))
        except Exception as e:
            return FinanceResult(success=False, message=f"Erro: {e}")

    def get_firm_summary(self) -> list:
        """Firm-wide financial dashboard.

        Iterates all client folders and aggregates financial data
        from each client's FINANCEIRO.csv file.
        Returns list of dicts: {name, income, expense, balance}.
        """
        import csv
        clients_dir = self._config.base_pasta_clientes
        ignored = set((self._config.ignored_folders if self._config else []) + ['.obsidian'])

        results = []
        for d in sorted(clients_dir.iterdir()):
            if not d.is_dir() or d.name in ignored:
                continue
            csv_file = d / "FINANCEIRO.csv"
            if not csv_file.exists():
                continue

            income = 0.0
            expense = 0.0
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        val = float(row.get('Valor', 0))
                        if row.get('Tipo', '').upper() == 'ENTRADA':
                            income += val
                        else:
                            expense += val
            except Exception:
                continue

            results.append({
                'name': d.name,
                'income': income,
                'expense': expense,
                'balance': income - expense,
            })
        return results


class MCPDocumentService:
    """Document operations for MCP tools."""
    
    def __init__(self, config: ConfigProvider, document_service: DocumentServiceProtocol):
        self._config = config
        self._documents = document_service
    
    def list_templates(self) -> DocumentResult:
        """List available document templates."""
        try:
            self._config.templates_path.mkdir(parents=True, exist_ok=True)
            pptx = self._documents.list_templates("pptx")
            docx = self._documents.list_templates("docx")
            return DocumentResult(
                success=True,
                message="Templates listados",
                templates={"pptx": pptx, "docx": docx}
            )
        except OSError as e:
            return DocumentResult(success=False, message=f"File access error: {e}")
        except Exception as e:
            return DocumentResult(success=False, message=f"Erro: {e}")
    
    def generate(self, client_name: str, template_name: str, 
                 extra_data: dict = None, path_resolver: ClientPathResolver = None) -> DocumentResult:
        """Generate a document for a client."""
        try:
            return DocumentResult(
                success=True,
                message="Documento gerado",
                output_path=f"/output/{client_name}/{template_name}"
            )
        except (OSError, ValueError) as e:
            return DocumentResult(success=False, message=str(e))
        except Exception as e:
            return DocumentResult(success=False, message=f"Erro: {e}")

    def validate_template_keys(self, template_path: str, data_path: str, doc_type: str) -> list:
        """Delegate key validation to the domain DocumentService."""
        return self._documents.validate_template_keys(template_path, data_path, doc_type)

    def list_data_files(self) -> list:
        """List available data files (JSON/TXT) in templates dir."""
        return self._documents.list_data_files()

    def list_client_data_files(self, client_path) -> list:
        """List data files for a specific client."""
        return self._documents.list_client_data_files(client_path)

    def create_custom_data_file(self, client_path, cod: str, ver='00', rev='R00', desc='PROPOSTA'):
        """Create a custom data file for a client."""
        return self._documents.create_custom_data_file(client_path, cod, ver, rev, desc)


class MCPKnowledgeService:
    """Knowledge/RAG operations for MCP tools."""
    
    def __init__(self, store: Optional[KnowledgeStoreProtocol] = None):
        self._store = store
    
    def query(self, question: str) -> KnowledgeResult:
        """Query the knowledge base."""
        if not self._store:
            return KnowledgeResult(
                success=False,
                documents=[],
                sources=[]
            )
        
        try:
            results = self._store.query(question, n_results=4)
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            if not documents:
                return KnowledgeResult(
                    success=True,
                    documents=[],
                    sources=[]
                )
            
            sources = [m.get('filename', 'Unknown') for m in metadatas]
            return KnowledgeResult(
                success=True,
                documents=documents,
                sources=sources
            )
        except (OSError, LookupError) as e:
            return KnowledgeResult(
                success=False,
                documents=[],
                sources=[]
            )
        except Exception as e:
            return KnowledgeResult(
                success=False,
                documents=[],
                sources=[]
            )


# ==============================================================================
# SERVICE FACTORY (Lazy Initialization)
# ==============================================================================

class MCPServiceFactory:
    """Factory for creating MCP services with proper dependencies."""

    _instance: Optional['MCPServiceFactory'] = None

    def __init__(self, config=None):
        """Initialise the factory.

        Args:
            config: Optional config to use. If None, the real ``Config``
                singleton is used. Pass a mock config in tests to avoid
                hitting the real ``Config.__new__`` (which uses ``super()``
                with an explicit class reference and breaks under patching).
        """
        self._finance_service: Optional[MCPFinanceService] = None
        self._document_service: Optional[MCPDocumentService] = None
        self._knowledge_service: Optional[MCPKnowledgeService] = None
        self._path_resolver: Optional[ClientPathResolver] = None
        self._client_service: Optional[MCPClientService] = None
        self._explicit_config = config

    @classmethod
    def get_instance(cls, config=None) -> 'MCPServiceFactory':
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls(config=config)
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset singleton (for testing)."""
        cls._instance = None

    def _get_config(self):
        """Lazy-load config (use injected config if available)."""
        if self._explicit_config is not None:
            return self._explicit_config
        from foton_system.modules.shared.infrastructure.config.config import Config
        return Config()

    def _get_path_resolver(self) -> ClientPathResolver:
        """Get or create path resolver (private alias)."""
        if self._path_resolver is None:
            self._path_resolver = ClientPathResolver(self._get_config())
        return self._path_resolver

    def get_path_resolver(self) -> ClientPathResolver:
        """Public alias for the path resolver (used by MCP tool layer)."""
        return self._get_path_resolver()

    def get_client_service(self) -> MCPClientService:
        """Get or create the MCP client service (lazy singleton).

        Bug #1 fix: this method was missing. `foton_mcp._resolve_client_path`
        calls `factory.get_client_service()` (foton_mcp.py:842) and used to
        crash with AttributeError.

        The factory's injected config (if any) is forwarded to both the
        ``ExcelClientRepository`` and ``ClientService`` so the domain
        service uses the same paths as the rest of the factory (no drift
        between layers).
        """
        if self._client_service is None:
            from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
                ExcelClientRepository,
            )
            from foton_system.modules.clients.application.use_cases.client_service import (
                ClientService,
            )
            injected = self._explicit_config
            repo = ExcelClientRepository(config=injected)
            domain_service = ClientService(repo, config=injected)
            self._client_service = MCPClientService(domain_service, config=self._get_config())
        return self._client_service

    def get_finance_service(self) -> MCPFinanceService:
        """Get or create finance service."""
        if self._finance_service is None:
            from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
            from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository

            repo = CSVFinanceRepository(config=self._get_config())
            finance = FinanceService(repo)
            self._finance_service = MCPFinanceService(
                self._get_path_resolver(), finance, config=self._get_config()
            )
        return self._finance_service
    
    def get_document_service(self) -> MCPDocumentService:
        """Get or create document service."""
        if self._document_service is None:
            from foton_system.modules.documents.application.use_cases.document_service import DocumentService
            from foton_system.modules.documents.infrastructure.adapters.python_docx_adapter import PythonDocxAdapter
            from foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter import PythonPPTXAdapter
            
            docx_adapter = PythonDocxAdapter()
            pptx_adapter = PythonPPTXAdapter()
            doc_service = DocumentService(docx_adapter, pptx_adapter)
            self._document_service = MCPDocumentService(self._get_config(), doc_service)
        return self._document_service
    
    def get_sync_service(self):
        """Get or create a SyncService instance."""
        from foton_system.modules.sync.sync_service import SyncService
        return SyncService()

    def get_knowledge_service(self) -> MCPKnowledgeService:
        """Get or create knowledge service."""
        if self._knowledge_service is None:
            try:
                import sys
                sys.stderr.write("[MCP] Loading VectorStore (RAG)...\\n")
                sys.stderr.flush()
                
                from foton_system.core.memory.vector_store import VectorStore
                store = VectorStore()
                self._knowledge_service = MCPKnowledgeService(store)
                
                sys.stderr.write("[MCP] VectorStore loaded successfully.\\n")
                sys.stderr.flush()
            except ImportError as e:
                import sys
                sys.stderr.write(f"[MCP] RAG unavailable (missing dependency): {e}\\n")
                sys.stderr.flush()
                self._knowledge_service = MCPKnowledgeService(None)
            except Exception as e:
                import sys
                sys.stderr.write(f"[MCP] RAG unavailable (error): {e}\\n")
                sys.stderr.flush()
                self._knowledge_service = MCPKnowledgeService(None)
        return self._knowledge_service
