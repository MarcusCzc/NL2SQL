"""
Execute prediction .sql files and compare with gold results.
k=1: single result per question (e.g. q000.sql); k>1: pass@k (files like q000_1.sql ... q000_k.sql).
Correctness: result row sets must match exactly, no tolerance.
SQL execution timeout 30s, timeout counted as error.
Result CSVs saved as qxxx_x format, 1-indexed (e.g. q000.sql -> q000_1.csv).
"""

import argparse
import json
import re
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Process, Queue
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pandas as pd
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent.parent
SQL_TIMEOUT = 30.0


def get_gold_sql_and_db(meta_by_id: Dict[str, Dict[str, Any]], instance_id: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (db_id, gold_sql) for the question from metadata; (None, None) if invalid."""
    rec = meta_by_id.get(instance_id)
    if not rec:
        return None, None
    return rec.get("db_id"), (rec.get("SQL") or "").strip()


def _execute_sql_worker(db_path: Union[Path, str], sql: str, result_queue: Queue) -> None:
    """Subprocess executes SQL, puts result in result_queue. Reads from disk, no copy to memory."""
    try:
        conn = sqlite3.connect(str(db_path), timeout=60)
        try:
            df = pd.read_sql_query(sql, conn)
            result_queue.put(("ok", df))
        finally:
            conn.close()
    except Exception as e:
        result_queue.put(("err", str(e)))


def execute_sql_to_dataframe(
    db_path: Path, sql: str, timeout: float = SQL_TIMEOUT
) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Execute SQL on SQLite and return DataFrame. Timeout 30s counted as error. Returns (df, None) on success, (None, error_msg) on failure."""
    q: Queue = Queue()
    p = Process(target=_execute_sql_worker, args=(db_path, sql, q))
    p.start()
    p.join(timeout=timeout)
    if p.is_alive():
        p.terminate()
        p.join(timeout=2.0)
        if p.is_alive():
            p.kill()
        return None, f"Timeout (exceeded {int(timeout)}s)"
    if q.empty():
        return None, "Process error"
    status, payload = q.get()
    if status == "ok":
        return payload, None
    return None, payload


@lru_cache(maxsize=None)
def load_gold_csv(file_path: Union[Path, str]) -> pd.DataFrame:
    """Load gold result CSV (cached) for comparison with predictions."""
    return pd.read_csv(file_path)


def load_jsonl_to_dict(jsonl_path: Path) -> Dict[str, Any]:
    """Parse JSONL into {instance_id: entry} dict."""
    data_dict: Dict[str, Any] = {}
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            data_dict[item["instance_id"]] = item
    return data_dict


def extract_sql_query(text: str) -> str:
    """Extract ```sql ... ``` code block from text; if none, return stripped full text."""
    m = re.search(r"```sql\n(.*?)\n```", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def get_sqlite_path(data_dir: Path, db_name: str) -> Path:
    """Return SQLite path under data dir: {db_id}/{db_id}.sqlite."""
    return data_dir / db_name / f"{db_name}.sqlite"


def df_to_result_set(df: pd.DataFrame) -> Set[tuple]:
    """Convert DataFrame to result row set for set-equality comparison."""
    return set(tuple(row) for row in df.itertuples(index=False, name=None))


def parse_sql_stem(stem: str) -> Tuple[str, int]:
    """Parse SQL file stem to (base_id, suffix). e.g. q000 -> (q000, 1), q000_3 -> (q000, 3). All 1-indexed."""
    m = re.match(r"^(.+)_(\d+)$", stem)
    if m:
        return m.group(1), int(m.group(2))
    return stem, 1


def _run_sql_and_compare(
    base_id: str,
    pred_sql_path: Path,
    meta_by_id: Dict[str, Dict[str, Any]],
    data_dir: Path,
    result_csv_dir: Path,
    result_csv_stem: str,
    gold_result_dir: Optional[Path] = None,
) -> Tuple[int, Optional[str]]:
    """
    Execute prediction and compare with gold (prefer existing gold CSV, else execute gold SQL).
    Optionally write prediction result CSV.

    Returns:
        (score, error_info), error_info is None if no error.
    """
    try:
        gold_path = gold_result_dir / f"{base_id}.csv" if gold_result_dir else None

        db_name, gold_sql = get_gold_sql_and_db(meta_by_id, base_id)
        if not db_name:
            return 0, "No gold for instance_id"
        if gold_path and gold_path.exists():
            gold_set = df_to_result_set(load_gold_csv(gold_path))
        else:
            if not gold_sql:
                return 0, "No gold SQL for instance_id"
            sqlite_path = get_sqlite_path(data_dir, db_name)
            if not sqlite_path.exists():
                return 0, f"Database not found: {sqlite_path}"
            gold_pd, gold_err = execute_sql_to_dataframe(sqlite_path, gold_sql)
            if gold_err:
                return 0, f"Gold SQL error: {gold_err}"
            gold_set = df_to_result_set(gold_pd)

        sqlite_path = get_sqlite_path(data_dir, db_name)
        if not sqlite_path.exists():
            return 0, f"Database not found: {sqlite_path}"

        pred_sql = extract_sql_query(pred_sql_path.read_text(encoding="utf-8"))
        pred_pd, pred_err = execute_sql_to_dataframe(sqlite_path, pred_sql)
        if pred_err:
            return 0, pred_err

        result_csv_dir.mkdir(parents=True, exist_ok=True)
        pred_pd.to_csv(result_csv_dir / f"{result_csv_stem}.csv", index=False)

        score = 1 if df_to_result_set(pred_pd) == gold_set else 0
        return score, "Result mismatch" if score == 0 else None
    except Exception as e:
        return 0, str(e)


def evaluate_single_sql_file(
    sql_file_stem: str,
    pred_sql_dir: Path,
    meta_by_id: Dict[str, Dict[str, Any]],
    data_dir: Path,
    result_csv_dir: Path,
    gold_result_dir: Optional[Path] = None,
) -> Tuple[str, int, int]:
    """Evaluate one SQL file; returns (base_id, suffix, score). Saves CSV as {base_id}_{suffix}.csv."""
    base_id, suffix = parse_sql_stem(sql_file_stem)
    csv_stem = f"{base_id}_{suffix}"
    pred_path = pred_sql_dir / f"{sql_file_stem}.sql"
    score, _ = _run_sql_and_compare(
        base_id, pred_path, meta_by_id, data_dir, result_csv_dir, csv_stem, gold_result_dir
    )
    return (base_id, suffix, score)


def run_evaluation(args: argparse.Namespace) -> List[Dict[str, Any]]:
    """Main evaluation flow; unified handling for all .sql files."""
    k = getattr(args, "k", 1)
    gold_dir = Path(args.gold_dir)
    if not gold_dir.is_absolute():
        gold_dir = (BASE_DIR / args.gold_dir).resolve()
    dataset_dir = gold_dir.parent
    data_dir = dataset_dir / "data"
    stem = dataset_dir.name
    eval_path = gold_dir / f"{stem}_eval.jsonl"
    metadata_path = gold_dir / f"{stem}_metadata.jsonl"
    gold_result_dir = gold_dir / "exec_result"
    pred_sql_dir = Path(args.sql_dir)
    if not pred_sql_dir.is_absolute():
        pred_sql_dir = (BASE_DIR / args.sql_dir).resolve()

    if not pred_sql_dir.is_dir():
        raise FileNotFoundError(f"Prediction directory not found: {pred_sql_dir}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")
    if not eval_path.exists():
        raise FileNotFoundError(f"Eval file not found: {eval_path}")

    gold_ids = list(load_jsonl_to_dict(eval_path).keys())
    meta_by_id = load_jsonl_to_dict(metadata_path)

    result_csv_dir = pred_sql_dir.parent / "csv"
    Path(result_csv_dir).mkdir(parents=True, exist_ok=True)

    all_stems = [f.stem for f in pred_sql_dir.glob("*.sql")]
    base_ids = set()
    for s in all_stems:
        base_id, _ = parse_sql_stem(s)
        base_ids.add(base_id)
    eval_ids = sorted(base_ids & set(gold_ids))
    if not eval_ids:
        print("No predictions overlap with gold (expect .sql like q000.sql or q000_1.sql ... q000_k.sql).")
        return []

    stems_to_eval = [s for s in all_stems if parse_sql_stem(s)[0] in eval_ids]
    scores_by_file: Dict[Tuple[str, int], int] = {}
    with ThreadPoolExecutor(max_workers=min(args.max_workers, len(stems_to_eval))) as ex:
        future_to_stem = {
            ex.submit(
                evaluate_single_sql_file,
                s, pred_sql_dir, meta_by_id, data_dir, result_csv_dir, gold_result_dir,
            ): s
            for s in stems_to_eval
        }
        for fut in tqdm(as_completed(future_to_stem), total=len(future_to_stem), desc="Evaluating"):
            base_id, suffix, score = fut.result()
            scores_by_file[(base_id, suffix)] = score

    def suffixes_for_base(base_id: str) -> List[int]:
        return sorted(s for (bid, s) in scores_by_file.keys() if bid == base_id)

    passed_ids = [
        iid for iid in eval_ids
        if any(scores_by_file.get((iid, s), 0) == 1 for s in suffixes_for_base(iid)[:k])
    ]
    acc = len(passed_ids) / len(eval_ids)
    print(f"Pass@{k}: {acc:.4f} ({len(passed_ids)}/{len(eval_ids)})")
    pd.DataFrame({"instance_id": passed_ids}).to_csv(Path(pred_sql_dir).parent / f"ids_pass@{k}.csv", index=False)
    return []


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Evaluate NL2SQL predictions against gold results")
    ap.add_argument("--k", type=int, default=1, help="Candidates per question; 1=single result, >1=pass@k (files like q000_1.sql ... q000_k.sql)")
    ap.add_argument("--sql_dir", default="example_submission_folder", help="Directory containing prediction .sql files (relative to project root if not absolute)")
    ap.add_argument("--gold_dir",default="gold",help="Gold directory with {stem}_eval.jsonl, {stem}_metadata.jsonl, exec_result/ (e.g. dataset/xxx/gold)",
    )
    ap.add_argument("--max_workers", type=int, default=8, help="Parallel evaluation threads")
    args = ap.parse_args()

    run_evaluation(args)
