#!/usr/bin/env python3
"""Script para gerar/atualizar o templates_index.json.

Usage:
    python scripts/build_templates_index.py <caminho_do_diretorio_de_templates>

Escaneia o diretório, coleta todos os arquivos .pptx e .docx,
e cria/atualiza o templates_index.json. Descrições existentes são
preservadas; templates novos recebem descrição vazia para edição manual.
"""

import json
import sys
from pathlib import Path


def build_index(templates_dir: Path) -> list[dict]:
    templates_dir = Path(templates_dir)
    if not templates_dir.is_dir():
        print(f"Erro: diretório não encontrado: {templates_dir}")
        sys.exit(1)

    index_file = templates_dir / "templates_index.json"

    existing = {}
    if index_file.exists():
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                existing = {entry["filename"]: entry for entry in data if "filename" in entry}
                print(f"Index existente carregado: {len(existing)} entradas.")
        except (json.JSONDecodeError, OSError) as e:
            print(f"Aviso: não foi possível ler index existente ({e}). Criando novo.")

    template_files = sorted(templates_dir.glob("*.pptx")) + sorted(templates_dir.glob("*.docx"))

    new_index = []
    new_entries = 0
    for tf in template_files:
        fname = tf.name
        if fname in existing:
            entry = existing[fname]
        else:
            entry = {
                "filename": fname,
                "description": "",
                "category": _infer_category(fname),
                "tags": [],
                "version": "1.0",
            }
            new_entries += 1
        new_index.append(entry)

    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(new_index, f, indent=2, ensure_ascii=False)

    print(f"Index salvo: {index_file}")
    print(f"Total: {len(new_index)} templates ({len(existing)} existentes, {new_entries} novos).")

    if new_entries:
        print("\n⚠️  Novos templates sem descrição. Edite manualmente o campo 'description' no index.")


def _infer_category(filename: str) -> str:
    name = filename.upper()
    if "PROPOSTA" in name:
        return "proposta"
    if "CONTRATO" in name:
        return "contrato"
    if "BRIEFING" in name:
        return "briefing"
    if "MEMORIAL" in name:
        return "memorial"
    if "PORTIFOLIO" in name:
        return "portifolio"
    if "APRESENT" in name:
        return "apresentacao"
    if "MISSAO" in name or "VISAO" in name or "VALORES" in name:
        return "administrativo"
    if "AUTORIZ" in name:
        return "autorizacao"
    if "TERMO" in name:
        return "termo"
    if "RECIBO" in name:
        return "recibo"
    return "outros"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    build_index(Path(sys.argv[1]))