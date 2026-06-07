"""
FotonFileSystemEventHandler - Watcher Proativo

Monitora mudanças no sistema de arquivos e:
1. Reindexação automática no banco vetorial (RAG)
2. Emissão de sugestões proativas ao usuário

DESIGN NOTES:
- Lazy loading de dependências RAG para não travar se chromadb não existir
- Debounce para evitar eventos duplicados (comum no Windows)
- Análise de contexto do arquivo alterado para sugestões inteligentes
"""

from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
from typing import Optional
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()

# Padrões de arquivos que disparam sugestões proativas
INFO_PATTERNS = {
    'INFO-': {
        'icon': '📋',
        'message': 'Dados do cadastro foram alterados.',
        'suggestion': 'Deseja regenerar documentos pendentes? (Use menu Documentos)'
    },
    'INFO-CLIENTE': {
        'icon': '👤',
        'message': 'Dados do cliente foram atualizados.',
        'suggestion': 'Verifique se há contratos ou propostas que precisam ser regenerados.'
    },
    'INFO-SERVICO': {
        'icon': '🔧',
        'message': 'Dados do serviço foram atualizados.',
        'suggestion': 'Considere atualizar a proposta financeira com os novos dados.'
    },
}


class FotonFileSystemEventHandler(FileSystemEventHandler):
    """
    Handles file system events to trigger proactive agent actions.
    Mainly: Re-indexing memory when documentation changes + suggestions.

    Note: VectorStore dependencies are loaded lazily to prevent crashes
    if chromadb/sentence-transformers are not installed.
    """

    def __init__(self) -> None:
        """Inicializa o handler com debounce e flag de disponibilidade RAG."""
        self.last_triggered: dict[str, float] = {}
        self.debounce_seconds: float = 2.0
        self._op_indexer = None
        self._rag_available: Optional[bool] = None

    def _is_rag_available(self) -> bool:
        """Check if RAG/VectorStore dependencies are available."""
        if self._rag_available is not None:
            return self._rag_available

        try:
            from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge
            self._op_indexer = OpIndexKnowledge(actor="Watcher_Service")
            self._rag_available = True
            logger.info("Watcher: RAG/VectorStore disponível.")
        except ImportError as e:
            self._rag_available = False
            logger.warning(f"Watcher: RAG indisponível (dependência faltando: {e}). Modo degradado ativado.")
        except Exception as e:
            self._rag_available = False
            logger.warning(f"Watcher: RAG indisponível ({e}). Modo degradado ativado.")

        return self._rag_available

    def _should_process(self, event) -> bool:
        """Filtra eventos por tipo (diretório), extensão (.md/.txt) e aplica debounce."""
        if event.is_directory:
            return False

        path = Path(event.src_path)

        if path.suffix.lower() not in ['.md', '.txt']:
            return False

        now = time.time()
        last = self.last_triggered.get(event.src_path, 0)
        if now - last < self.debounce_seconds:
            return False

        self.last_triggered[event.src_path] = now
        return True

    def _analyze_for_suggestions(self, file_path: str) -> None:
        """
        Analisa o arquivo alterado e emite sugestões proativas.
        Verifica se é um arquivo INFO-* e sugere ações relevantes.
        """
        path = Path(file_path)
        filename = path.name.upper()

        # Verificar padrões de INFO mais específicos primeiro
        matched = None
        for pattern in sorted(INFO_PATTERNS.keys(), key=len, reverse=True):
            if pattern in filename:
                matched = INFO_PATTERNS[pattern]
                break

        if matched:
            client_folder = path.parent.name
            print(f"\n{'='*60}")
            print(f"  {matched['icon']}  SUGESTÃO PROATIVA - {client_folder}")
            print(f"{'='*60}")
            print(f"  {matched['message']}")
            print(f"  💡 {matched['suggestion']}")
            print(f"  📄 Arquivo: {path.name}")
            print(f"{'='*60}\n")
            logger.info(f"Sugestão proativa emitida para: {path.name} em {client_folder}")

    def on_modified(self, event) -> None:
        """Callback acionado em modificação de arquivo — dispara análise e reindexação."""
        if self._should_process(event):
            print(f"👀 Watcher detectou modificação: {Path(event.src_path).name}")
            self._analyze_for_suggestions(event.src_path)
            self._trigger_index(event.src_path)

    def on_created(self, event) -> None:
        """Callback acionado em criação de arquivo — dispara análise e reindexação."""
        if self._should_process(event):
            print(f"👀 Watcher detectou criação: {Path(event.src_path).name}")
            self._analyze_for_suggestions(event.src_path)
            self._trigger_index(event.src_path)

    def _trigger_index(self, file_path: str) -> None:
        """Dispara reindexação no banco vetorial via OpIndexKnowledge (se RAG disponível)."""
        if not self._is_rag_available():
            logger.debug(f"Arquivo ignorado (RAG indisponível): {file_path}")
            return

        try:
            target_folder = Path(file_path).parent
            print(f"🧠 Atualizando Memória para contexto: {target_folder.name}...")

            res = self._op_indexer.execute(target_path=str(target_folder))

            print(f"✅ Memória Atualizada! ({res.get('chunks_created', 0)} chunks processados)")

        except Exception as e:
            logger.error(f"Watcher Error during indexing: {e}", exc_info=True)
            print(f"❌ Erro no Watcher: {e}")


