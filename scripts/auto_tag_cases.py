"""
自动标注 NL2SQL 测试用例脚本

基于人工标注 65 题的经验，使用 LLM 自动分析 200 个 case，检查：
1. Evidence 是否有错误（E_tag）
2. 题目是否有歧义（Q_Tag）
3. GT SQL 是否有问题（Tag）
4. 各模型（Gemini/Claude/GLM 等）生成的 SQL 是否有问题（{Model}_Tag）

输出格式与 llms_failed_passat1.json 一致（扁平 JSON，Tag 作为顶层字段）。
输出目录按模型名组织：auto_tag_output/{MODEL}/tagged_cases_{时间戳}.json

调用 .env 中配置的 API KEY。支持断点续跑。

用法:
  python auto_tag_cases.py                                     # 标注全部 200 题（仅GT）
  python auto_tag_cases.py --limit 10                          # 只标注前 10 题
  python auto_tag_cases.py --resume                            # 断点续跑
  python auto_tag_cases.py --model gpt-4o                      # 指定调用的LLM
  python auto_tag_cases.py --debug                             # 记录完整 prompt
  python auto_tag_cases.py --review-models claude,gemini,glm   # 同时审查模型SQL
  python auto_tag_cases.py --input llms_failed_passat1.json    # 从已有文件加载模型SQL
  python auto_tag_cases.py --review-models claude,gemini,glm --input llms_failed_passat1.json
"""

import json
import os
import re
import sys
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path
from textwrap import dedent

# ---------- .env 加载 ----------
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
except ImportError:
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for _line in f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip())

MODEL = os.getenv("MODEL", "gpt-4o")
PROVIDER = os.getenv("PROVIDER", "openai")
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://api.chatanywhere.tech/v1")

# ---------- 数据路径（修改） ----------
BASE_DIR = SCRIPT_DIR / "sample200_passatk"
GOLD_DIR = BASE_DIR / "gold"
METADATA_JSONL = GOLD_DIR / "sample200_metadata.jsonl"
ECOM_BIRD_ROOT = SCRIPT_DIR / "ecommerce_data" / "ecommerce_bird"
TABLES_JSON = ECOM_BIRD_ROOT / "tables.json"

# ---------- 标注参考（错误模式 + 精简示例，合并为紧凑格式） ----------
TAG_REFERENCE = dedent("""
    ## 已知 GT 错误模式及示例

    | # | 错误模式 | 示例输入(摘要) | 示例输出 |
    |---|----------|---------------|---------|
    | 1 | 缺 DISTINCT 去重 | Q:"1997年有多少订单通过mail运送?" GT:`COUNT(l_orderkey)` | `{"Tag":"wrong case, 没有使用COUNT(DISTINCT l_orderkey)"}` |
    | 2 | 只查了1个region表(superstore有4个) | Q:"Alejandro Grove订购了哪些产品?" GT:只查`west_superstore` | `{"Tag":"wrong case, 没有查询所有region表"}` |
    | 3 | JOIN条件不完整 | Q:"计算prom brushed steel产品平均利润" GT:`partsupp JOIN lineitem ON ps_suppkey=l_suppkey` | `{"Tag":"wrong case, JOIN缺少ps_partkey=l_partkey"}` |
    | 4 | 缺少WHERE过滤条件 | Q:"East superstore标准运输的家具数量?" GT:缺`Category='Furniture'` | `{"Tag":"wrong SQL, GT没有查询Furniture条件"}` |
    | 5 | 排序字段错误 | Q:"最高债务供应商的国家?" GT:`ORDER BY s_suppkey` | `{"Tag":"wrong case, 应用s_acctbal排序而非s_suppkey"}` |
    | 6 | 字符串/ID拼写错误 | Q:"Road-650, Red, 60的总成本?" GT:`Name='Road-650 Red, 60'`(缺逗号) | `{"Tag":"wrong case, 产品名缺少逗号"}` |
    | 7 | 聚合逻辑错误 | Q:"购买最多产品的客户?" GT:`ORDER BY单笔金额`而非`GROUP BY客户SUM总额` | `{"Tag":"wrong case, 应GROUP BY客户并SUM总金额"}` |
    | 8 | 多余WHERE条件 | Q:"德国供应商百分比?" GT:多出`s_acctbal<0` | `{"Tag":"wrong case, 多出s_acctbal<0条件"}` |
    | 9 | 百分比vs比率混淆 | Q:"Texas和Indiana客户比率?" GT:多乘了100 | `{"Tag":"wrong case, ratio不需乘100"}` |
    | 10 | LIMIT/SELECT字段错误 | Q:"最低余额前5国家?" GT:`LIMIT 1` | `{"Tag":"wrong case, LIMIT应为5"}` |
    | 11 | Evidence日期/大小写错误 | Q:"4月每日平均发货量?" evidence写1月 | `{"Tag":"wrong case, 应为4月非1月","E_tag":"wrong evidence, 日期范围错误"}` |
    | 12 | Evidence大小写与数据不一致 | Q:"非洲的国家?" evidence:`r_name='Africa'` 实际`'AFRICA'` | `{"E_tag":"wrong evidence, 应为AFRICA全大写"}` |
    | 13 | 题目歧义 | Q:"印度高于平均余额的客户?" 全球平均or印度平均不明确 | `{"Tag":"wrong case, 缺n_name='INDIA'","Q_Tag":"平均值范围有争议"}` |
    | 14 | 无问题 | Q:"伦敦有多少客户?" GT:`COUNT(CustomerID) WHERE City='London'` | `{}` |

    ### 注意
    - Tag 表示 GT SQL 有错，格式: "wrong case, 描述"
    - E_tag 表示 evidence 有错，格式: "wrong evidence, 描述"
    - Q_Tag 表示题目有歧义，直接描述争议
    - 一个 case 可同时有多种 tag
    - 没有问题则输出空对象 `{}`
    - **不要过度标注**，只标注确切的问题
""").strip()


def load_questions():
    if not METADATA_JSONL.exists():
        print(f"错误: 找不到 {METADATA_JSONL}")
        sys.exit(1)
    return [json.loads(line) for line in METADATA_JSONL.read_text(encoding="utf-8").strip().split("\n") if line.strip()]


def load_schema(db_id):
    if not TABLES_JSON.exists():
        return ""
    try:
        tables_data = json.loads(TABLES_JSON.read_text(encoding="utf-8"))
    except Exception:
        return ""
    schema = next((s for s in tables_data if s.get("db_id") == db_id), None)
    if not schema:
        return ""

    table_names = schema.get("table_names_original", [])
    column_names = schema.get("column_names_original", [])
    column_types = schema.get("column_types", [])
    primary_keys = schema.get("primary_keys", [])
    foreign_keys = schema.get("foreign_keys", [])
    flat_col = [(p[0], p[1]) for p in column_names]

    type_idx = 0
    table_to_cols = {}
    for p in column_names:
        tid, cname = p[0], p[1]
        if cname == "*":
            continue
        t = column_types[type_idx] if type_idx < len(column_types) else ""
        type_idx += 1
        table_to_cols.setdefault(tid, []).append((cname, t))

    table_pk = {}
    for item in primary_keys:
        for pk_idx in (item if isinstance(item, list) else [item]):
            if isinstance(pk_idx, int) and pk_idx < len(flat_col):
                tid, cname = flat_col[pk_idx]
                if cname != "*":
                    table_pk.setdefault(tid, []).append(cname)

    table_fk = {}
    for ci, pi in foreign_keys:
        if ci < len(flat_col) and pi < len(flat_col):
            ctid, ccol = flat_col[ci]
            ptid, pcol = flat_col[pi]
            pt = table_names[ptid] if ptid < len(table_names) else ""
            if pt and ccol != "*":
                table_fk.setdefault(ctid, []).append(f"{ccol} -> {pt}.{pcol}")

    parts = []
    for idx, tname in enumerate(table_names):
        cols = table_to_cols.get(idx, [])
        block = f"Table {tname} ({', '.join(f'{c} {t}' for c, t in cols)})"
        if table_pk.get(idx):
            block += "\n  PK: " + ", ".join(table_pk[idx])
        if table_fk.get(idx):
            block += "\n  FK: " + "; ".join(table_fk[idx])
        parts.append(block)

    result = "\n\n".join(parts)
    return result[:50000] + "\n...[truncated]" if len(result) > 50000 else result


def call_llm(prompt, temperature=0, max_retries=3):
    if not API_KEY:
        raise RuntimeError("API_KEY 未配置，请检查 .env 文件")
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY, **({"base_url": BASE_URL} if BASE_URL else {}))

    for attempt in range(max_retries):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return r.choices[0].message.content or ""
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 30 * (attempt + 1)
                print(f"  API 失败 (第{attempt+1}次): {e}, {wait}s 后重试...")
                time.sleep(wait)
            else:
                raise


def build_tag_prompt(case, schema_text):
    fid = case["instance_id"]
    evidence = case.get("evidence", "")
    prompt = dedent(f"""
        你是一个 NL2SQL 质量审计专家。请仔细分析以下测试用例，判断：1) Evidence 是否有错误 2) 题目是否有歧义 3) Ground Truth SQL 是否有问题。

        ## 数据库 Schema
        {schema_text}

        ## 测试用例
        - **Instance ID**: {fid}
        - **数据库**: {case["db_id"]}
        - **问题**: {case["question"]}
        - **Evidence**: {evidence if evidence else "(无)"}
        - **Ground Truth SQL**:
        ```sql
        {case["SQL"]}
        ```

        {TAG_REFERENCE}

        ## 你的任务

        请逐步分析：1) Evidence 是否有错误 2) 题目是否有歧义 3) GT SQL 是否有问题。然后输出一个 JSON 对象（用 ```json ``` 包裹），可包含 `Tag`、`E_tag`、`Q_Tag`。
        只包含发现问题的字段，没有问题则输出 `{{}}`。
    """).strip()
    return prompt


def build_full_review_prompt(case, schema_text, review_models, model_data):
    """构建同时审查 GT SQL 和各模型 SQL 的 prompt"""
    fid = case["instance_id"]
    evidence = case.get("evidence", "")

    # 构建模型 SQL 部分
    model_sql_sections = []
    for m in review_models:
        sql_key = f"{m}_sql"
        sql_val = model_data.get(sql_key, "")
        if not sql_val:
            continue
        correct_key = f"{m}_correct"
        correct_val = model_data.get(correct_key, "unknown")
        m_cap = m.capitalize()
        model_sql_sections.append(
            f"### {m_cap} 生成的 SQL（pass@1 正确性: {correct_val}）\n"
            f"```sql\n{sql_val}\n```"
        )

    model_sql_block = "\n\n".join(model_sql_sections) if model_sql_sections else "(无模型 SQL 数据)"

    # 构建模型 tag 输出说明
    model_tag_names = [f"{m.capitalize()}_Tag" for m in review_models if model_data.get(f"{m}_sql")]
    model_tag_desc = ", ".join(f'`{t}`' for t in model_tag_names) if model_tag_names else "(无)"

    prompt = dedent(f"""
        你是一个 NL2SQL 质量审计专家。请仔细分析以下测试用例，判断：
        1. Evidence 是否有错误
        2. 题目是否有歧义
        3. Ground Truth SQL 是否有问题
        4. 各模型生成的 SQL 是否有问题（独立判断每个模型的 SQL 正确性）

        ## 数据库 Schema
        {schema_text}

        ## 测试用例
        - **Instance ID**: {fid}
        - **数据库**: {case["db_id"]}
        - **问题**: {case["question"]}
        - **Evidence**: {evidence if evidence else "(无)"}
        - **Ground Truth SQL**:
        ```sql
        {case["SQL"]}
        ```

        ## 各模型生成的 SQL

        {model_sql_block}

        {TAG_REFERENCE}

        ## 模型 SQL 审查补充规则

        除了审查 GT SQL 以外，请同时审查上述每个模型生成的 SQL。对于每个模型：
        - 如果模型 SQL 有错误，输出 `{{{{Model}}}}_Tag` 字段，格式: "wrong SQL, 描述"
        - 模型可能犯和 GT 相同的错误（如缺少 DISTINCT），此时标注: "wrong SQL, 与GT相同问题，描述"
        - 模型可能犯独有的错误（如使用了错误的聚合函数、拼写错误等）
        - 如果模型 SQL 正确（即使 pass@1 判为 false），不需要输出该模型的 Tag
        - 注意：pass@1 判为 false 不等于 SQL 有逻辑错误，可能是结果格式不同等原因
        - **不要过度标注**，只标注确切的逻辑错误

        ## 你的任务

        请逐步分析，然后输出一个 JSON 对象（用 ```json ``` 包裹），可包含以下字段：
        - `Tag`: GT SQL 有错
        - `E_tag`: Evidence 有错
        - `Q_Tag`: 题目有歧义
        - {model_tag_desc}: 对应模型 SQL 有错

        只包含发现问题的字段，没有问题则输出 `{{{{}}}}`.
    """).strip()
    return prompt


def parse_llm_response(text):
    m = re.search(r"```json\s*\n(.*?)\n```", text, re.DOTALL)
    json_str = m.group(1).strip() if m else None
    if not json_str:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        json_str = m.group(0) if m else None
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None


def setup_logging(log_dir, debug=False):
    log_file = log_dir / "auto_tag.log"
    logger = logging.getLogger("auto_tag")
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)
    logger.handlers.clear()

    fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    fh.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def build_output_entry(case, tags_dict, review_models=None, model_data=None):
    """构建与 llms_failed_passat1.json 格式一致的扁平输出"""
    entry = {
        "db_id": case["db_id"],
        "instance_id": case["instance_id"],
        "question": case["question"],
        "evidence": case.get("evidence", ""),
        "SQL": case["SQL"],
    }
    # GT 相关 tag
    for field in ["Tag", "E_tag", "Q_Tag"]:
        if field in tags_dict and tags_dict[field]:
            entry[field] = tags_dict[field]
    # 模型 SQL 和模型 Tag
    if review_models and model_data:
        for m in review_models:
            sql_key = f"{m}_sql"
            correct_key = f"{m}_correct"
            tag_key = f"{m.capitalize()}_Tag"
            if sql_key in model_data:
                entry[sql_key] = model_data[sql_key]
            if correct_key in model_data:
                entry[correct_key] = model_data[correct_key]
            if tag_key in tags_dict and tags_dict[tag_key]:
                entry[tag_key] = tags_dict[tag_key]
    return entry


def main():
    parser = argparse.ArgumentParser(description="自动标注 NL2SQL 测试用例")
    parser.add_argument("--limit", type=int, default=0, help="限做前 N 题，0=全部")
    parser.add_argument("--resume", action="store_true", help="断点续跑")
    parser.add_argument("--model", type=str, default=None, help="覆盖 .env 中的模型")
    parser.add_argument("--output", type=str, default=None, help="输出文件路径")
    parser.add_argument("--start", type=int, default=0, help="从第 N 题开始（0-indexed）")
    parser.add_argument("--debug", action="store_true", help="记录完整 prompt 到日志")
    parser.add_argument("--review-models", type=str, default=None,
                        help="要审查SQL的模型列表，逗号分隔，如: claude,gemini,glm")
    parser.add_argument("--input", type=str, default=None,
                        help="包含模型SQL的JSON文件路径（如 llms_failed_passat1.json）")
    args = parser.parse_args()

    global MODEL
    if args.model:
        MODEL = args.model

    # ---------- 解析 review-models ----------
    review_models = []
    if args.review_models:
        review_models = [m.strip().lower() for m in args.review_models.split(",") if m.strip()]
        print(f"将审查以下模型的 SQL: {', '.join(review_models)}")

    # ---------- 加载模型 SQL 数据 ----------
    model_sql_index = {}  # instance_id -> {claude_sql: ..., gemini_sql: ..., ...}
    if args.input:
        input_path = Path(args.input) if os.path.isabs(args.input) else SCRIPT_DIR / args.input
        if input_path.exists():
            try:
                input_data = json.loads(input_path.read_text(encoding="utf-8"))
                for item in input_data:
                    fid = item.get("instance_id", "")
                    if fid:
                        model_sql_index[fid] = item
                print(f"从 {input_path.name} 加载了 {len(model_sql_index)} 条模型 SQL 数据")
            except Exception as e:
                print(f"⚠️ 无法加载 input 文件: {e}")
        else:
            print(f"⚠️ input 文件不存在: {input_path}")

    # 输出路径：auto_tag_output/{MODEL}/tagged_cases_{时间戳}.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = SCRIPT_DIR / "auto_tag_output" / MODEL
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = output_dir / f"tagged_cases_{timestamp}.json"

    logger = setup_logging(output_dir, debug=args.debug)
    logger.info("=" * 80)
    logger.info(f"自动标注开始 - 模型: {MODEL}")
    logger.info(f"输出目录: {output_dir}")
    logger.info(f"输出文件: {output_file}")

    # 加载题目
    questions = load_questions()
    total = len(questions)
    print(f"共加载 {total} 道题目")
    print(f"模型: {MODEL}")
    print(f"输出: {output_dir}")

    if args.start > 0:
        questions = questions[args.start:]
        print(f"从第 {args.start} 题开始")
    if args.limit > 0:
        questions = questions[:args.limit]
        print(f"限制处理 {len(questions)} 题")

    # 断点续跑
    existing_results = {}
    if args.resume:
        if output_file.exists():
            try:
                for item in json.loads(output_file.read_text(encoding="utf-8")):
                    existing_results[item["instance_id"]] = item
                print(f"已加载 {len(existing_results)} 条已有结果")
            except Exception as e:
                print(f"无法加载: {e}")
        for lf in sorted(output_dir.glob("tagged_cases_*.json"), reverse=True):
            try:
                for item in json.loads(lf.read_text(encoding="utf-8")):
                    if item["instance_id"] not in existing_results:
                        existing_results[item["instance_id"]] = item
                print(f"从 {lf.name} 补充，共 {len(existing_results)} 条")
            except Exception:
                pass

    schema_cache = {}
    results = []
    success_count = error_count = skip_count = issue_count = 0

    try:
        from tqdm import tqdm
        progress = tqdm(questions, desc="标注进度")
    except ImportError:
        progress = questions

    for q in progress:
        fid = q["instance_id"]
        db_id = q["db_id"]

        if args.resume and fid in existing_results:
            results.append(existing_results[fid])
            skip_count += 1
            continue

        if db_id not in schema_cache:
            schema_cache[db_id] = load_schema(db_id)

        # 获取模型 SQL 数据（如果有）
        model_data = model_sql_index.get(fid, {})

        # 根据是否有 review_models 选择 prompt
        if review_models and model_data:
            prompt = build_full_review_prompt(q, schema_cache[db_id], review_models, model_data)
        else:
            prompt = build_tag_prompt(q, schema_cache[db_id])

        try:
            print(f"\n[{fid}] 正在分析: {q['question'][:60]}...")
            logger.info(f"[{fid}] 开始分析")
            if args.debug:
                logger.debug(f"[{fid}] 完整 prompt:\n{prompt}")

            resp = call_llm(prompt, temperature=0)
            logger.info(f"[{fid}] 模型响应:\n{resp}")

            tags_dict = parse_llm_response(resp)
            if tags_dict is None:
                print(f"  ⚠️ 无法解析响应")
                logger.warning(f"[{fid}] JSON 解析失败")
                tags_dict = {}

            entry = build_output_entry(q, tags_dict, review_models, model_data)
            results.append(entry)
            success_count += 1

            # 检测所有 tag 字段（GT + 模型）
            all_tag_keys = ["Tag", "E_tag", "Q_Tag"]
            if review_models:
                all_tag_keys += [f"{m.capitalize()}_Tag" for m in review_models]
            has_tag = any(k in entry for k in all_tag_keys)
            if has_tag:
                issue_count += 1
                print(f"  🔴 发现问题:")
                for k in all_tag_keys:
                    if k in entry:
                        print(f"    - [{k}] {entry[k]}")
            else:
                print(f"  ✅ 无问题")

            logger.info(f"[{fid}] 完成 - has_issue={has_tag}")

        except Exception as e:
            error_count += 1
            print(f"  ❌ 错误: {e}")
            logger.error(f"[{fid}] 错误: {e}", exc_info=True)
            entry = build_output_entry(q, {}, review_models, model_data)
            entry["_error"] = str(e)
            results.append(entry)

        # 每题保存
        output_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(1)

    # 最终保存
    output_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"标注完成！")
    print(f"  总题数: {total} | 已处理: {success_count} | 跳过: {skip_count} | 错误: {error_count}")
    print(f"  发现问题: {issue_count}")
    print(f"  输出文件: {output_file}")
    print("=" * 60)

    logger.info(f"标注完成 - 处理:{success_count} 跳过:{skip_count} 错误:{error_count} 发现问题:{issue_count}")

    # 生成摘要
    summary_file = output_dir / f"tag_summary_{timestamp}.md"
    generate_summary(results, summary_file)
    print(f"  摘要文件: {summary_file}")


def generate_summary(results, summary_file):
    e_tags, q_tags, gt_tags = [], [], []
    # 自动检测所有模型 Tag 字段
    model_tag_keys = set()
    for item in results:
        for k in item:
            if k.endswith("_Tag") and k not in ("E_tag", "Q_Tag", "Tag"):
                model_tag_keys.add(k)

    model_tags = {k: [] for k in sorted(model_tag_keys)}

    for item in results:
        base = {"instance_id": item["instance_id"], "db_id": item.get("db_id", "")}
        if "E_tag" in item:
            e_tags.append({**base, "desc": item["E_tag"]})
        if "Q_Tag" in item:
            q_tags.append({**base, "desc": item["Q_Tag"]})
        if "Tag" in item:
            gt_tags.append({**base, "desc": item["Tag"]})
        for k in model_tag_keys:
            if k in item:
                model_tags[k].append({**base, "desc": item[k]})

    md = [
        f"# NL2SQL 自动标注结果摘要\n",
        f"> 模型: {MODEL} | 题数: {len(results)} | 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "---\n",
        f"## 一、Evidence 错误（{len(e_tags)} 条）\n",
    ]
    if e_tags:
        md += ["| 题号 | 数据库 | 描述 |", "|------|--------|------|"]
        md += [f"| {t['instance_id']} | {t['db_id']} | {t['desc']} |" for t in e_tags]
    else:
        md.append("无\n")

    md += ["", f"## 二、题目争议（{len(q_tags)} 条）\n"]
    if q_tags:
        md += ["| 题号 | 数据库 | 描述 |", "|------|--------|------|"]
        md += [f"| {t['instance_id']} | {t['db_id']} | {t['desc']} |" for t in q_tags]
    else:
        md.append("无\n")

    md += ["", f"## 三、GT 有问题（{len(gt_tags)} 条）\n"]
    if gt_tags:
        md += ["| 题号 | 数据库 | 描述 |", "|------|--------|------|"]
        md += [f"| {t['instance_id']} | {t['db_id']} | {t['desc']} |" for t in gt_tags]
    else:
        md.append("无\n")

    # 各模型 SQL 错误
    section_num = 4
    for tag_key in sorted(model_tag_keys):
        model_name = tag_key.replace("_Tag", "")
        tag_list = model_tags[tag_key]
        section_num += 1
        section_label = chr(ord('A') + section_num - 5)  # A, B, C...
        md += ["", f"## 三-{section_label}、{model_name} SQL 有问题（{len(tag_list)} 条）\n"]
        if tag_list:
            md += ["| 题号 | 数据库 | 描述 |", "|------|--------|------|"]
            md += [f"| {t['instance_id']} | {t['db_id']} | {t['desc']} |" for t in tag_list]
        else:
            md.append("无\n")

    # 统计
    all_tag_keys_for_stat = ["Tag", "E_tag", "Q_Tag"] + sorted(model_tag_keys)
    issue_cases = sum(1 for r in results if any(k in r for k in all_tag_keys_for_stat))
    md += [
        "\n---\n", "## 统计\n",
        "| 指标 | 数值 |", "|------|------|",
        f"| 总题数 | {len(results)} |",
        f"| 有问题的 case 数 | {issue_cases} |",
        f"| Evidence 错误 | {len(e_tags)} |",
        f"| 题目争议 | {len(q_tags)} |",
        f"| GT 错误 | {len(gt_tags)} |",
    ]
    for tag_key in sorted(model_tag_keys):
        model_name = tag_key.replace("_Tag", "")
        md.append(f"| {model_name} SQL 错误 | {len(model_tags[tag_key])} |")

    summary_file.write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    main()
