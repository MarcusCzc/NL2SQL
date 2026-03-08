"""
Generate metadata and evaluation config JSONL files from input question JSON.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def get_gold_dir(input_path: Path) -> Path:
    """Gold dir is sibling of input's parent (e.g. data/ -> gold/ under same dataset)."""
    return input_path.parent.parent / "gold"


def load_questions(path: Path) -> List[Dict[str, Any]]:
    """Load question JSON; index i maps to instance_id q{i:03d}."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_metadata(questions: List[Dict[str, Any]], metadata_out: Path, eval_out: Path) -> None:
    """Write metadata and eval JSONL files for each question."""
    metadata_out.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_out, "w", encoding="utf-8") as mf, open(eval_out, "w", encoding="utf-8") as ef:
        for i, q in enumerate(questions):
            instance_id = f"q{i:03d}"
            meta = {
                "instance_id": instance_id,
                "db_id": q.get("db_id",""),
                "question": q.get("question", ""),
                "evidence": q.get("evidence", ""),
                "SQL": (q.get("SQL") or "").strip(),
            }
            mf.write(json.dumps(meta, ensure_ascii=False) + "\n")
            eval_row = {"instance_id": instance_id, "condition_cols": [], "ignore_order": True}
            ef.write(json.dumps(eval_row, ensure_ascii=False) + "\n")
    print(f"Wrote {metadata_out} and {eval_out}, total {len(questions)} questions.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate metadata and eval JSONL files from question JSON."
    )
    parser.add_argument(
        "--input_json",
        type=Path,
        required=True,
        help="Path to input question JSON file.",
    )
    args = parser.parse_args()
    input_path = args.input_json.resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    gold_dir = get_gold_dir(input_path)
    stem = input_path.stem
    metadata_out = gold_dir / f"{stem}_metadata.jsonl"
    eval_out = gold_dir / f"{stem}_eval.jsonl"

    questions = load_questions(input_path)
    build_metadata(questions, metadata_out, eval_out)


if __name__ == "__main__":
    main()
