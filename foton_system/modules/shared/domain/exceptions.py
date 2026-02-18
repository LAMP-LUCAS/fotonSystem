"""
Domain Exceptions for FotonSystem.

These exceptions provide specific error types for better error handling
and debugging throughout the application.
"""


class FotonError(Exception):
    """Base exception for all FotonSystem errors."""
    pass


# --- Client Errors ---

class ClientNotFoundError(FotonError):
    """Raised when a client cannot be found."""
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"Cliente não encontrado: {identifier}")


class InvalidAliasError(FotonError):
    """Raised when a client alias is invalid."""
    def __init__(self, alias: str, reason: str = "contém caracteres inválidos"):
        self.alias = alias
        super().__init__(f"Alias inválido '{alias}': {reason}")


class DuplicateClientError(FotonError):
    """Raised when trying to create a client that already exists."""
    def __init__(self, alias: str):
        self.alias = alias
        super().__init__(f"Cliente já existe com alias: {alias}")


# --- Database Errors ---

class DatabaseConnectionError(FotonError):
    """Raised when unable to connect to the database."""
    def __init__(self, path: str, reason: str = ""):
        self.path = path
        msg = f"Erro ao conectar com a base de dados: {path}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class DatabaseLockError(FotonError):
    """Raised when the database file is locked by another process."""
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Base de dados bloqueada (possivelmente aberta em outro programa): {path}")


class DataIntegrityError(FotonError):
    """Raised when data integrity is compromised."""
    def __init__(self, message: str):
        super().__init__(f"Erro de integridade de dados: {message}")


# --- Document Errors ---

class TemplateNotFoundError(FotonError):
    """Raised when a template file cannot be found."""
    def __init__(self, template_name: str):
        self.template_name = template_name
        super().__init__(f"Template não encontrado: {template_name}")


class DocumentGenerationError(FotonError):
    """Raised when document generation fails."""
    def __init__(self, reason: str):
        super().__init__(f"Erro ao gerar documento: {reason}")


# --- Validation Errors ---

class ValidationError(FotonError):
    """Raised when validation fails."""
    def __init__(self, field: str, reason: str):
        self.field = field
        super().__init__(f"Validação falhou para '{field}': {reason}")
