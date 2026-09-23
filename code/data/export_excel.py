"""按需从 MySQL 导出清洗后的手机数据到 Excel。

这个脚本只用于人工查看数据，不进入正式数据处理流程。
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pymysql

from data.excel_exporter import export_excel


def main() -> None:
    parser = argparse.ArgumentParser(description="从 MySQL 导出手机数据到 Excel")
    parser.add_argument("--out", type=Path, default=Path("data/phones_clean.xlsx"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default="phone_recommender")
    args = parser.parse_args()

    connection = pymysql.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        charset="utf8mb4",
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM phones_clean")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
    connection.close()
    frame = pd.DataFrame(rows, columns=columns)

    output = export_excel(frame, args.out)
    print(f"已从 MySQL 导出 {len(frame)} 条数据到：{output}")


if __name__ == "__main__":
    main()
