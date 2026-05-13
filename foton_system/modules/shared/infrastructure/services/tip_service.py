"""
TipService - O "Cérebro Didático" do Foton System.
Extrai pílulas de conhecimento da documentação para exibir na UI.
"""

import re
import random
from pathlib import Path
from typing import List, Dict, Optional
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager

class TipService:
    def __init__(self):
        self.docs_dir = PathManager._find_project_root() / "docs"
        self.tip_pattern = re.compile(r'>\s*\[!DIDACTIC:(\w+)\]\s*(.*)', re.IGNORECASE)
        self._tips_cache: Dict[str, List[str]] = {}
        self._is_indexed = False

    def _index_tips(self):
        """Varre a documentação e indexa todas as dicas encontradas."""
        if not self.docs_dir.exists():
            return

        self._tips_cache = {"GERAL": []}
        
        # Busca em todos os arquivos .md da pasta docs
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = self.tip_pattern.findall(content)
                    for context, message in matches:
                        ctx = context.upper()
                        if ctx not in self._tips_cache:
                            self._tips_cache[ctx] = []
                        self._tips_cache[ctx].append(message.strip())
            except Exception:
                continue
        
        self._is_indexed = True

    def get_random_tip(self, context: str = "GERAL") -> str:
        """Retorna uma dica aleatória baseada no contexto."""
        if not self._is_indexed:
            self._index_tips()

        ctx = context.upper()
        
        # Tenta o contexto específico, senão busca no geral
        tips = self._tips_cache.get(ctx, [])
        if not tips and ctx != "GERAL":
            tips = self._tips_cache.get("GERAL", [])
            
        if not tips:
            return "Dica: Mantenha seus arquivos INFO atualizados para propostas precisas."
            
        return random.choice(tips)

    def get_all_tips(self) -> List[str]:
        """Retorna todas as dicas disponíveis em todos os contextos."""
        if not self._is_indexed:
            self._index_tips()
        
        all_tips = []
        for ctx_tips in self._tips_cache.values():
            all_tips.extend(ctx_tips)
        return all_tips
