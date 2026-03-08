"""
Ecommerce-Bird-sample200 dataset adapter: tables.json + database_description CSV schema, metadata JSONL.
"""

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from .base import BaseAdapter

_tables_cache: Dict[str, list] = {}


def _get_tables_data(data_dir: Path) -> list:
    """Load tables.json from data_dir; cached per data_dir."""
    key = str(data_dir.resolve())
    if key not in _tables_cache:
        tables_path = data_dir / "tables.json"
        if tables_path.exists():
            try:
                _tables_cache[key] = json.loads(tables_path.read_text(encoding="utf-8"))
            except Exception:
                _tables_cache[key] = []
        else:
            _tables_cache[key] = []
    return _tables_cache[key]


@lru_cache(maxsize=256)
def _load_schema(db_id: str, data_dir: Path, max_chars: int = 1000000) -> str:
    """Build schema text for db_id from tables.json and database_description."""
    tables_data = _get_tables_data(data_dir)
    schema = next((s for s in tables_data if s.get("db_id") == db_id), None)
    if not schema:
        return ""

    table_names_original = schema.get("table_names_original", [])
    column_names_original = schema.get("column_names_original", [])
    column_types = schema.get("column_types", [])
    primary_keys = schema.get("primary_keys", [])
    foreign_keys = schema.get("foreign_keys", [])
    desc_dir = data_dir / db_id / "database_description"

    flat_col = [(pair[0], pair[1]) for pair in column_names_original]
    type_idx = 0
    table_to_cols: Dict[int, List[tuple]] = {}
    for pair in column_names_original:
        tid, cname = pair[0], pair[1]
        if cname == "*":
            continue
        t = column_types[type_idx] if type_idx < len(column_types) else ""
        type_idx += 1
        table_to_cols.setdefault(tid, []).append((cname, t))

    table_pk: Dict[int, List[str]] = {}
    for item in primary_keys:
        indices = item if isinstance(item, list) else [item]
        for pk_idx in indices:
            if isinstance(pk_idx, int) and pk_idx < len(flat_col):
                tid, cname = flat_col[pk_idx][0], flat_col[pk_idx][1]
                if cname != "*":
                    table_pk.setdefault(tid, []).append(cname)
    table_fk: Dict[int, List[str]] = {}
    for child_idx, parent_idx in foreign_keys:
        if child_idx < len(flat_col) and parent_idx < len(flat_col):
            ctid, ccol = flat_col[child_idx][0], flat_col[child_idx][1]
            ptid, pcol = flat_col[parent_idx][0], flat_col[parent_idx][1]
            parent_table = table_names_original[ptid] if ptid < len(table_names_original) else ""
            if parent_table and ccol != "*":
                table_fk.setdefault(ctid, []).append(f"{ccol} -> {parent_table}.{pcol}")

    parts = []
    for table_idx, tname in enumerate(table_names_original):
        table_cols = table_to_cols.get(table_idx, [])
        cols_str = ", ".join(f"{c} {t}" for c, t in table_cols)
        col_desc_map: Dict[str, List[str]] = {}
        desc_path = desc_dir / f"{tname}.csv"
        if desc_path.exists():
            with open(desc_path, "r", encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    orig = row.get("original_column_name", "").strip()
                    if orig == "*":
                        continue
                    col_desc = (row.get("column_description") or "").strip()
                    val_desc = (row.get("value_description") or "").strip()
                    col_desc_map[orig] = [p for p in (col_desc, val_desc) if p]
        desc_lines = []
        for cname, ctype in table_cols:
            type_tag = f" ({ctype})" if ctype else ""
            if cname in col_desc_map and col_desc_map[cname]:
                desc_lines.append(f"  - {cname}{type_tag}: {' | '.join(col_desc_map[cname])}")
            else:
                desc_lines.append(f"  - {cname}{type_tag}" if type_tag else f"  - {cname}")

        block = f"Table {tname} ({cols_str})"
        if table_pk.get(table_idx):
            block += "\n  Primary key: " + ", ".join(table_pk[table_idx])
        if table_fk.get(table_idx):
            block += "\n  Foreign key: " + "; ".join(table_fk[table_idx])
        if desc_lines:
            block += "\n" + "\n".join(desc_lines)
        parts.append(block)

    result = "\n\n".join(parts)
    if len(result) > max_chars:
        result = result[:max_chars] + "\n\n... [truncated]"
    return result


class EcommerceBirdAdapter(BaseAdapter):
    """Adapter for ecommerce_bird_sample200: tables.json schema, database_description CSVs, metadata JSONL."""

    def load_questions(self, gold_dir: Path) -> List[Dict[str, Any]]:
        """Load from {stem}_metadata.jsonl where stem = parent dir name."""
        stem = gold_dir.parent.name
        metadata_path = gold_dir / f"{stem}_metadata.jsonl"
        if not metadata_path.exists():
            return []
        questions = []
        for line in metadata_path.read_text(encoding="utf-8").strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                questions.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return questions

    def build_prompt(self, q: Dict[str, Any], data_dir: Path) -> str:
        """Schema + optional Hint(evidence) + Question; no few-shot examples."""
        db_id = q.get("db_id") or q.get("db")
        question = q.get("question") or q.get("instruction", "")
        evidence = q.get("evidence", "")
        schema_text = _load_schema(db_id, data_dir)

        prompt = [
            "You are a SQLite expert. Given the database schema below, write a SQL query "
            "to answer the question.\n\n"
            "### Database Schema\n"
            f"{schema_text}\n"
        ]
        if evidence:
            prompt.append(f"\n### Hint\n{evidence}")
        prompt.append(
            f"\n### Question\n{question}\n\n"
            "### SQL\nWrite only the SQL query with no explanation.\n\n"
            "SQL:"
        )
        return "\n".join(prompt)
