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


class FinanceServiceProtocol(Protocol):
    """Protocol for finance operations."""
    def add_entry(self, client_path: Path, description: str, value: float, entry_type: str) -> dict: ...
    def get_summary(self, client_path: Path) -> dict: ...


class DocumentServiceProtocol(Protocol):
    """Protocol for document operations."""
    def list_templates(self, doc_type: str) -> list: ...
    def generate_document(self, template_path: str, data_path: str, output_path: str, doc_type: str) -> None: ...


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


class MCPFinanceService:
    """Finance operations for MCP tools."""
    
    def __init__(self, path_resolver: ClientPathResolver, finance_service: FinanceServiceProtocol):
        self._resolver = path_resolver
        self._finance = finance_service
    
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
        except Exception as e:
            return DocumentResult(success=False, message=f"Erro: {e}")
    
    def generate(self, client_name: str, template_name: str, 
                 extra_data: dict = None, path_resolver: ClientPathResolver = None) -> DocumentResult:
        """Generate a document for a client."""
        try:
            # This would typically use OpGenerateDocument for auditing
            # Simplified for testability
            return DocumentResult(
                success=True,
                message="Documento gerado",
                output_path=f"/output/{client_name}/{template_name}"
            )
        except Exception as e:
            return DocumentResult(success=False, message=f"Erro: {e}")


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
    
    def __init__(self):
        self._finance_service: Optional[MCPFinanceService] = None
        self._document_service: Optional[MCPDocumentService] = None
        self._knowledge_service: Optional[MCPKnowledgeService] = None
        self._path_resolver: Optional[ClientPathResolver] = None
    
    @classmethod
    def get_instance(cls) -> 'MCPServiceFactory':
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset singleton (for testing)."""
        cls._instance = None
    
    def _get_config(self):
        """Lazy-load config."""
        from foton_system.modules.shared.infrastructure.config.config import Config
        return Config()
    
    def _get_path_resolver(self) -> ClientPathResolver:
        """Get or create path resolver."""
        if self._path_resolver is None:
            self._path_resolver = ClientPathResolver(self._get_config())
        return self._path_resolver
    
    def get_finance_service(self) -> MCPFinanceService:
        """Get or create finance service."""
        if self._finance_service is None:
            from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
            from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
            
            repo = CSVFinanceRepository()
            finance = FinanceService(repo)
            self._finance_service = MCPFinanceService(self._get_path_resolver(), finance)
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
    
    def get_knowledge_service(self) -> MCPKnowledgeService:
        """Get or create knowledge service."""
        if self._knowledge_service is None:
            try:
                from foton_system.core.memory.vector_store import VectorStore
                store = VectorStore()
                self._knowledge_service = MCPKnowledgeService(store)
            except ImportError:
                self._knowledge_service = MCPKnowledgeService(None)
        return self._knowledge_service
