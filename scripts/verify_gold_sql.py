"""
Verify what ratio of gold (standard answer) SQL can be executed successfully.
Input: SQL directory (to derive dataset path). Gold SQL comes from metadata.
"""

import argparse
import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tqdm import tqdm

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
SQL_TIMEOUT = 30.0


def find_dataset_dir(sql_dir: Path) -> Path:
    """Walk up from sql_dir until we find a dir with gold/ and data/ subdirs."""
    p = sql_dir.resolve()
    while p != p.parent:
        if (p / "gold").is_dir() and (p / "data").is_dir():
            return p
        p = p.parent
    raise ValueError(f"Cannot find dataset root from {sql_dir}")


def load_jsonl_to_dict(jsonl_path: Path) -> Dict[str, Any]:
    """Parse JSONL into {instance_id: entry} dict."""
    result: Dict[str, Any] = {}
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            result[item["instance_id"]] = item
    return result


def execute_sql(db_path: Path, sql: str, timeout: float = SQL_TIMEOUT) -> Tuple[bool, Optional[str]]:
    """Execute SQL on SQLite. Returns (success, error_msg). Uses thread + join for timeout."""
    result: List[Tuple[bool, Optional[str]]] = []

    def worker() -> None:
        try:
            conn = sqlite3.connect(str(db_path), timeout=60)
            try:
                conn.execute(sql)
                result.append((True, None))
            finally:
                conn.close()
        except Exception as e:
            result.append((False, str(e)))

    t = threading.Thread(target=worker)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        return False, f"Timeout (exceeded {int(timeout)}s)"
    if not result:
        return False, "Thread error"
    return result[0]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify ratio of gold SQL that executes successfully."
    )
    parser.add_argument(
        "--sql_dir",
        type=Path,
        required=True,
        help="SQL directory (e.g. dataset/xxx/prediction/model/pass@1/sql) to derive dataset path.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of questions to verify (for quick testing).",
    )
    args = parser.parse_args()
    sql_dir = Path(args.sql_dir).resolve()
    limit = args.limit
    if not sql_dir.is_dir():
        raise FileNotFoundError(f"SQL directory not found: {sql_dir}")

    dataset_dir = find_dataset_dir(sql_dir)
    stem = dataset_dir.name
    gold_dir = dataset_dir / "gold"
    metadata_path = gold_dir / f"{stem}_metadata.jsonl"
    data_dir = dataset_dir / "data"

    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")

    meta_by_id = load_jsonl_to_dict(metadata_path)
    success = 0
    total = 0
    errors: list[Tuple[str, str]] = []

    items = list(meta_by_id.items())
    if limit is not None:
        items = items[:limit]
    for instance_id, rec in tqdm(items, desc="Verifying"):
        db_id = rec.get("db_id")
        sql = (rec.get("SQL") or "").strip()
        if not db_id or not sql:
            errors.append((instance_id, "Missing db_id or SQL"))
            total += 1
            continue
        db_path = data_dir / db_id / f"{db_id}.sqlite"
        if not db_path.exists():
            errors.append((instance_id, f"Database not found: {db_path}"))
            total += 1
            continue
        ok, err = execute_sql(db_path, sql)
        total += 1
        if ok:
            success += 1
        else:
            errors.append((instance_id, err or "Unknown error"))

    ratio = success / total if total else 0
    print(f"Executable ratio: {ratio:.2%} ({success}/{total})")
    if errors:
        print(f"\nFailed ({len(errors)}):")
        for iid, err in errors[:20]:
            print(f"  {iid}: {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
        failed_path = sql_dir.parent / "verify_gold_failed.jsonl"
        with open(failed_path, "w", encoding="utf-8") as f:
            for iid, err in errors:
                meta = meta_by_id.get(iid, {})
                f.write(
                    json.dumps(
                        {
                            "instance_id": iid,
                            "db_id": meta.get("db_id"),
                            "error": err,
                            "SQL": meta.get("SQL"),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        print(f"\nFailed cases saved to {failed_path}")


if __name__ == "__main__":
    main()
