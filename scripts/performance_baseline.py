"""
performance_baseline.py

Gera baseline de performance das operações do FotonSystem a partir do log
contínuo de telemetria (operation_log.jsonl).

Uso:
    python scripts/performance_baseline.py                  # Gera baseline
    python scripts/performance_baseline.py --diff           # Compara com baseline anterior
    python scripts/performance_baseline.py --days 7         # Últimos 7 dias
    python scripts/performance_baseline.py --days 30        # Últimos 30 dias

Arquitetura:
    Segue o padrão de Port/Adapter: a leitura do log (DataPort) é separada
    da análise (AnalysisPort) e da saída (OutputPort), permitindo trocar
    fontes de dados ou formatos de relatório sem alterar a lógica central.
"""

import argparse
import json
import math
import os
import statistics
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Garante que a raiz do projeto está no sys.path para imports relativos
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# ─── Config ─────────────────────────────────────────────────────────────────
METRICS_REL_DIR = Path(".opencode") / "metrics"
BASELINE_PREFIX = "performance_baseline"
LOG_FILE_NAME = "operation_log.jsonl"


# ─── Ports (interfaces abstratas) ───────────────────────────────────────────

class DataPort:
    """Interface para leitura de dados de telemetria."""
    def read_records(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError


class AnalysisPort:
    """Interface para análise estatística dos registros."""
    def compute_baseline(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        raise NotImplementedError

    def diff(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class OutputPort:
    """Interface para saída do relatório."""
    def write(self, path: Path, data: dict):
        raise NotImplementedError

    def display(self, baseline: Dict[str, Any], diff_data: Optional[Dict[str, Any]] = None):
        raise NotImplementedError


# ─── Adapters (implementações concretas) ─────────────────────────────────────

class JsonlDataAdapter(DataPort):
    """Lê registros do operation_log.jsonl usando PathManager."""

    def __init__(self, log_path: Optional[Path] = None):
        self._log_path = log_path

    def _resolve_log_path(self) -> Path:
        if self._log_path:
            return self._log_path
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        return PathManager.get_app_data_dir() / LOG_FILE_NAME

    def read_records(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        log_path = self._resolve_log_path()
        if not log_path.exists():
            print(f"[baseline] Log não encontrado: {log_path}")
            return []

        records = []
        cutoff = None
        if days is not None:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if cutoff is not None:
                    ts_str = record.get("timestamp", "")
                    try:
                        ts = datetime.fromisoformat(ts_str)
                        if ts < cutoff:
                            continue
                    except (ValueError, TypeError):
                        continue

                records.append(record)

        return records


class StatsAnalysisAdapter(AnalysisPort):
    """Análise estatística com média, p50, p95, min, max, desvio padrão."""

    def compute_baseline(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not records:
            return {"gerado_em": datetime.now(timezone.utc).isoformat(), "operacoes": {}}

        by_op: Dict[str, List[float]] = {}
        for r in records:
            op = r.get("operacao", "UNKNOWN")
            dur = r.get("duracao_ms")
            if dur is None:
                continue
            by_op.setdefault(op, []).append(dur)

        baseline: Dict[str, Any] = {}
        for op, durs in sorted(by_op.items()):
            durs.sort()
            n = len(durs)
            baseline[op] = {
                "count": n,
                "min_ms": round(min(durs), 2),
                "max_ms": round(max(durs), 2),
                "avg_ms": round(statistics.mean(durs), 2),
                "p50_ms": round(self._percentile(durs, 50), 2),
                "p95_ms": round(self._percentile(durs, 95), 2),
                "stddev_ms": round(statistics.stdev(durs), 2) if n > 1 else 0.0,
            }

        return {
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "total_registros": len(records),
            "operacoes": baseline,
        }

    def diff(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
        cur_ops = current.get("operacoes", {})
        prev_ops = previous.get("operacoes", {})
        diff_data: Dict[str, Any] = {}

        all_keys = set(cur_ops.keys()) | set(prev_ops.keys())
        for op in sorted(all_keys):
            c = cur_ops.get(op)
            p = prev_ops.get(op)
            entry: Dict[str, Any] = {}

            if c:
                entry["atual"] = dict(c)
            if p:
                entry["anterior"] = dict(p)
            if c and p:
                delta = {}
                for metric in ("avg_ms", "p50_ms", "p95_ms", "min_ms", "max_ms"):
                    cv = c.get(metric, 0)
                    pv = p.get(metric, 0)
                    delta[metric] = f"{cv:+.2f} ({(cv - pv) / pv * 100:+.1f}%)" if pv else f"{cv:+.2f}"
                entry["delta"] = delta
                entry["count_delta"] = c.get("count", 0) - p.get("count", 0)

            if op not in cur_ops:
                entry["status"] = "removida"
            elif op not in prev_ops:
                entry["status"] = "nova"

            diff_data[op] = entry

        dias = self._days_between(previous.get("gerado_em"), current.get("gerado_em"))
        return {
            "gerado_em": current.get("gerado_em"),
            "baseline_anterior": previous.get("gerado_em"),
            "dias_entre_baselines": dias,
            "operacoes": diff_data,
        }

    @staticmethod
    def _percentile(sorted_data: List[float], p: float) -> float:
        if not sorted_data:
            return 0.0
        k = (len(sorted_data) - 1) * p / 100.0
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_data[int(k)]
        return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)

    @staticmethod
    def _days_between(iso_a: Optional[str], iso_b: Optional[str]) -> int:
        if not iso_a or not iso_b:
            return 0
        try:
            a = datetime.fromisoformat(iso_a)
            b = datetime.fromisoformat(iso_b)
            return abs((b - a).days)
        except (ValueError, TypeError):
            return 0


class JsonOutputAdapter(OutputPort):
    """Salva baseline em JSON e exibe tabela no terminal."""

    def __init__(self, metrics_dir: Path):
        self._metrics_dir = Path(metrics_dir)

    def write(self, path: Path, data: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[baseline] Salvo: {path}")

    def display(self, baseline: Dict[str, Any], diff_data: Optional[Dict[str, Any]] = None):
        ops = baseline.get("operacoes", {})
        if not ops:
            print("[baseline] Nenhuma operação registrada no período.")
            return

        if diff_data:
            self._display_diff(diff_data)
        else:
            self._display_baseline(baseline)

    def _display_baseline(self, baseline: Dict[str, Any]):
        ops = baseline.get("operacoes", {})
        total = baseline.get("total_registros", 0)
        sep = "=" * 70
        dash = "-" * 70
        print(f"\n{sep}")
        print(f"  BASELINE DE PERFORMANCE  |  {total} registros analisados")
        print(f"{sep}")
        print(f"{'Operacao':<30} {'#':>5} {'Media(ms)':>10} {'P50(ms)':>9} {'P95(ms)':>9} {'Min(ms)':>8} {'Max(ms)':>8}")
        print(f"{dash}")
        for op, stats in sorted(ops.items()):
            print(
                f"{op:<30} {stats['count']:>5} "
                f"{stats['avg_ms']:>10.2f} {stats['p50_ms']:>9.2f} {stats['p95_ms']:>9.2f} "
                f"{stats['min_ms']:>8.2f} {stats['max_ms']:>8.2f}"
            )
        print(f"{dash}")

    def _display_diff(self, diff_data: Dict[str, Any]):
        ops = diff_data.get("operacoes", {})
        dias = diff_data.get("dias_entre_baselines", 0)
        sep2 = "=" * 80
        dash2 = "-" * 80
        print(f"\n{sep2}")
        print(f"  COMPARATIVO vs BASELINE ANTERIOR  |  {dias} dia(s) entre medicoes")
        print(f"{sep2}")
        for op, entry in sorted(ops.items()):
            status = entry.get("status", "")
            tag = " [NOVA]" if status == "nova" else " [REMOVIDA]" if status == "removida" else ""
            print(f"\n  {op}{tag}")
            curr = entry.get("atual", {})
            prev = entry.get("anterior", {})
            delta = entry.get("delta", {})

            if curr:
                print(f"    Atual:    {curr.get('count', 0)} ops | "
                      f"media {curr.get('avg_ms', 0):.1f}ms | "
                      f"p95 {curr.get('p95_ms', 0):.1f}ms")
            if prev:
                print(f"    Anterior: {prev.get('count', 0)} ops | "
                      f"media {prev.get('avg_ms', 0):.1f}ms | "
                      f"p95 {prev.get('p95_ms', 0):.1f}ms")
            if delta:
                print(f"    D media:  {delta.get('avg_ms', 'N/A')} | "
                      f"D p95:    {delta.get('p95_ms', 'N/A')}")
            if entry.get("count_delta", 0) != 0:
                print(f"    D volume: {entry['count_delta']:+d} operacoes")
        print(f"\n{dash2}")


# ─── Utilitário para localizar baseline anterior ─────────────────────────────

def _find_latest_baseline(metrics_dir: Path) -> Optional[Path]:
    if not metrics_dir.exists():
        return None
    candidates = sorted(metrics_dir.glob(f"{BASELINE_PREFIX}_*.json"), reverse=True)
    return candidates[0] if candidates else None


def _next_baseline_path(metrics_dir: Path) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    return metrics_dir / f"{BASELINE_PREFIX}_{today}.json"


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Performance baseline para operações do FotonSystem"
    )
    parser.add_argument(
        "--diff", action="store_true",
        help="Compara com baseline anterior (se existir)"
    )
    parser.add_argument(
        "--days", type=int, default=None,
        help="Apenas registros dos últimos N dias (ex: 7, 30)"
    )
    parser.add_argument(
        "--log-path", type=str, default=None,
        help="Caminho customizado para operation_log.jsonl (opcional)"
    )
    args = parser.parse_args()

    # Resolve diretório de métricas a partir da raiz do projeto
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    metrics_dir = project_root / METRICS_REL_DIR

    # ── Adapters ────────────────────────────────────────────────────────
    data_adapter = JsonlDataAdapter(
        log_path=Path(args.log_path) if args.log_path else None
    )
    analysis = StatsAnalysisAdapter()
    output = JsonOutputAdapter(metrics_dir)

    # ── Leitura ─────────────────────────────────────────────────────────
    print(f"[baseline] Lendo registros de telemetria...")
    records = data_adapter.read_records(days=args.days)
    if not records:
        print("[baseline] Nenhum registro encontrado.")
        sys.exit(0)

    print(f"[baseline] {len(records)} registro(s) carregados.")

    # ── Análise ─────────────────────────────────────────────────────────
    baseline = analysis.compute_baseline(records)

    # ── Diff (opcional) ─────────────────────────────────────────────────
    diff_data = None
    if args.diff:
        prev_path = _find_latest_baseline(metrics_dir)
        if prev_path:
            try:
                with open(prev_path, "r", encoding="utf-8") as f:
                    previous = json.load(f)
                diff_data = analysis.diff(baseline, previous)
                print(f"[baseline] Comparando com: {prev_path.name}")
            except (json.JSONDecodeError, OSError) as e:
                print(f"[baseline] Erro ao ler baseline anterior: {e}")
        else:
            print("[baseline] Nenhum baseline anterior encontrado. Gerando apenas o atual.")

    # ── Saída ───────────────────────────────────────────────────────────
    output.display(baseline, diff_data)

    # ── Persistência ────────────────────────────────────────────────────
    out_path = _next_baseline_path(metrics_dir)
    output.write(out_path, baseline)

    # Se houve diff, salva também o relatório de diff
    if diff_data:
        diff_path = out_path.with_name(out_path.stem + "_diff.json")
        output.write(diff_path, diff_data)

    print("[baseline] Concluído.")


if __name__ == "__main__":
    main()
