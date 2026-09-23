"""把 phones_raw.json 中的手机数据导入 SQLite 数据库。"""

import argparse
import json
from pathlib import Path

from data import database


def main() -> None:
    parser = argparse.ArgumentParser(description="导入手机数据到数据库")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/phones_raw.json"),
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/phone_recommender.db"),
    )
    args = parser.parse_args()

    records = json.loads(args.input.read_text(encoding="utf-8"))
    database.init_db(args.db)
    inserted = database.import_phones(records, db_path=args.db)
    total = database.count_phones(db_path=args.db)
    print(f"导入 {inserted} 条数据，数据库当前共有 {total} 条")


if __name__ == "__main__":
    main()
