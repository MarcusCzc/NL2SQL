"""
Generate NL2SQL predictions and optionally run evaluation.
k=1: single SQL per question; k>1: Pass@k (k SQL per question with temperature>0 for diversity).
API config loaded from environment variables: MODEL, PROVIDER, API_KEY, BASE_URL.
Dataset-specific prompt construction via adapters (--adapter).
"""

import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODEL = os.getenv("MODEL", "claude-opus-4-6-thinking")
PROVIDER = os.getenv("PROVIDER", "openai")
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "")

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent

PASSATK_TEMPERATURE = 0.7


def _resolve_path(path_str: str) -> Path:
    """Resolve path; relative paths are under BASE_DIR."""
    p = Path(path_str)
    if not p.is_absolute():
        p = (BASE_DIR / path_str).resolve()
    return p


def extract_sql(text: str) -> str:
    """Extract ```sql ... ``` block from model output; if none, return trimmed full text."""
    m = re.search(r"```sql\s*\n(.*?)\n```", text, re.DOTALL | re.I)
    return m.group(1).strip() if m else text.strip()


def call_llm(prompt: str, temperature: float = 0) -> str:
    """Call configured LLM; temperature>0 for pass@k diversity."""
    if not API_KEY:
        raise RuntimeError("API_KEY not set; configure via .env or environment variables")

    if PROVIDER in ("openai", "deepseek"):
        from openai import OpenAI

        kwargs = {"api_key": API_KEY}
        if PROVIDER == "deepseek" or BASE_URL:
            kwargs["base_url"] = BASE_URL or "https://api.deepseek.com"
        client = OpenAI(**kwargs)
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return r.choices[0].message.content or ""

    raise ValueError(f"Unknown provider: {PROVIDER}")


def _gen_one_sql(
    fid: str, prompt: str, suffix: int, fpath: Path, temperature: float
) -> None:
    """Single generation: call_llm -> extract_sql -> write file; for concurrent execution."""
    try:
        resp = call_llm(prompt, temperature=temperature)
        sql = extract_sql(resp)
        fpath.write_text(sql, encoding="utf-8")
    except Exception as e:
        print(f"\n[{fid}_{suffix}] {e}")
        fpath.write_text(f"-- Error: {e}", encoding="utf-8")


def main() -> None:
    import argparse
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from tqdm import tqdm

    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    from adapters import get_adapter

    ap = argparse.ArgumentParser(description="Generate NL2SQL predictions and optionally evaluate")
    ap.add_argument("--adapter", default="ecommerce_bird_sample200", help="Dataset adapter name")
    ap.add_argument("--k", type=int, default=1, help="SQL per question; 1=single, >1=Pass@k (default 1)")
    ap.add_argument("--batch_size", type=int, default=50, help="Concurrent tasks per batch when k>1")
    ap.add_argument("--limit", type=int, default=0, help="Process first N questions only; 0=all")
    ap.add_argument("--eval", action="store_true", help="Run evaluation after generation")
    ap.add_argument("--temperature", type=float, default=PASSATK_TEMPERATURE, help="LLM temperature (used when k>1)")
    ap.add_argument("--gold_dir", default="dataset/ecommerce_bird_sample200/gold", help="Gold directory")
    args = ap.parse_args()

    adapter = get_adapter(args.adapter)
    k = args.k
    gold_path = _resolve_path(args.gold_dir)
    dataset_dir = gold_path.parent
    data_dir = dataset_dir / "data"

    questions = adapter.load_questions(gold_path)
    if not questions:
        print(f"No questions loaded from {gold_path}")
        return
    if args.limit > 0:
        questions = questions[: args.limit]

    out_dir = dataset_dir / "prediction" / MODEL / f"pass@{k}" / "sql"
    out_dir.mkdir(parents=True, exist_ok=True)

    temperature = 0 if k == 1 else args.temperature

    for q in tqdm(questions, desc=f"Pass@{k}"):
        fid = q["instance_id"]
        prompt = adapter.build_prompt(q, data_dir)
        tasks = []
        for i in range(1, k + 1):
            fpath = out_dir / f"{fid}_{i}.sql"
            if fpath.exists():
                continue
            tasks.append((fid, prompt, i, fpath))
        if not tasks:
            continue
        batch_size = min(args.batch_size, len(tasks))
        for batch_start in range(0, len(tasks), batch_size):
            batch = tasks[batch_start : batch_start + batch_size]
            with ThreadPoolExecutor(max_workers=len(batch)) as ex:
                futures = {
                    ex.submit(_gen_one_sql, fid, prompt, i, fpath, temperature): (fid, i)
                    for fid, prompt, i, fpath in batch
                }
                for fut in as_completed(futures):
                    fut.result()

    print(f"Output saved to {out_dir}")

    if args.eval:
        eval_script = SCRIPT_DIR / "evaluate_passatk.py"
        if eval_script.exists():
            subprocess.run(
                [
                    sys.executable,
                    str(eval_script),
                    "--sql_dir", str(out_dir.resolve()),
                    "--gold_dir", str(gold_path.resolve()),
                    "--k", str(k),
                    "--max_workers", "8",
                ],
                cwd=str(BASE_DIR),
            )
        else:
            print("evaluate_passatk.py not found, skipping eval")


if __name__ == "__main__":
    main()
