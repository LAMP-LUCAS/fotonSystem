from abc import ABC, abstractmethod

class DocumentServicePort(ABC):
    @abstractmethod
    def load_document(self, path: str):
        pass

    @abstractmethod
    def save_document(self, document, path: str):
        pass

    @abstractmethod
    def replace_text(self, document, replacements: dict):
        pass
