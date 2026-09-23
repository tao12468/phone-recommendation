"""数据清洗流水线入口。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from data.clean_rules import clean_records
from data.mysql_writer import write_to_mysql


def main() -> None:
    parser = argparse.ArgumentParser(description="清洗手机数据并写入 MySQL")
    parser.add_argument("--input", type=Path, default=Path("data/phones_raw.json"))
    parser.add_argument("--output-json", type=Path, default=Path("data/phones_clean.json"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default="phone_recommender")
    parser.add_argument("--skip-db", action="store_true", help="只清洗，不写入 MySQL")
    args = parser.parse_args()

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    cleaned = clean_records(raw)

    print(f"原始数据：{len(raw)} 条")
    print(f"清洗后：{len(cleaned)} 条")
    print("主要字段缺失数量：")
    for column in ["price", "screen_size", "battery", "cpu", "ram", "rom"]:
        missing = int(cleaned[column].isna().sum())
        print(f"{column}: {missing}")

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_json(args.output_json, orient="records", force_ascii=False, indent=2)

    if not args.skip_db:
        count = write_to_mysql(
            cleaned,
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database,
        )
        print(f"已清洗并写入 MySQL：{count} 条")
    else:
        print(f"已清洗：{len(cleaned)} 条，未写入 MySQL")

if __name__ == "__main__":
    main()
