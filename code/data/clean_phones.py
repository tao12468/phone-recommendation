"""清洗手机原始数据，并写入 MySQL。

流程：
原始 JSON -> Pandas 清洗 -> 清洗结果 JSON -> MySQL -> 可选 Excel
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd
import pymysql
from crawler.zol_spider import guess_brand


SCHEMA = Path(__file__).with_name("schema_mysql.sql").read_text(encoding="utf-8")


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def clean_cpu(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    text = re.sub(r"更多.*$", "", text)
    text = re.sub(r"手机性能排行.*$", "", text)
    return text.strip(" ，,>")


def clean_core_count(value) -> str:
    return clean_text(value).strip(" >")


def clean_usage_scenes(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    text = text.replace(">", " ").replace("，", " ").replace(",", " ")
    tokens = [item for item in text.split() if item not in {"", "，", ","}]
    return ",".join(tokens)


def extract_product_name(value) -> str:
    """只保留手机型号名称，去掉颜色、内存、宣传语等描述。"""

    if pd.isna(value):
        return ""
    text = str(value).strip()

    # 优先匹配型号名称后面紧跟的内存版本，例如：
    # (12GB/256GB)、（256GB）、（8G）、（国际版/双4G）。
    match = re.search(
        r"^(.*?\(\d+\s*(?:GB|TB|G)[^)]*\)|.*?（[^）]*(?:GB|G|国际版|全网通)[^）]*）)",
        text,
    )
    if match:
        return match.group(1).strip()

    # 没有明确的型号版本括号时，在常见宣传语开始前截断。
    description_markers = [
        "iPhone的",
        "外观设计",
        "手机制式",
        "蔡司",
        "骁龙",
        "天玑",
        "麒麟",
        "徕卡",
        "HarmonyOS",
        "沉浸",
        "圆弧",
        "超薄",
        "大电池",
        "金标",
        "蓝晶",
        "超视网膜",
    ]
    match = re.search(rf"\s*({'|'.join(description_markers)})", text)
    if match:
        return text[: match.start()].strip()

    # 只有很短的名字时，直接保留全部，避免误删产品名。
    if len(text) <= 60:
        return text.strip()

    return text[:120].strip()


def valid_number(value, low: float, high: float) -> float | None:
    if pd.isna(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number < low or number > high:
        return None
    return round(number, 2)


def clean_records(records: list[dict]) -> pd.DataFrame:
    """把原始记录清洗成适合入库的 DataFrame。"""

    frame = pd.DataFrame(records)
    frame = frame.rename(columns={"id": "source_id"})

    if "brand" not in frame:
        frame["brand"] = ""
    frame["brand"] = frame["brand"].fillna("")
    frame["brand"] = frame.apply(
        lambda row: row["brand"] or guess_brand(row.get("name", "")),
        axis=1,
    )

    frame["name"] = frame["name"].apply(extract_product_name).str.slice(0, 200)
    frame = frame[frame["name"].str.len() > 0]
    frame["price"] = frame["price"].apply(lambda value: valid_number(value, 1, 200000))
    frame["screen_size"] = frame["screen_size"].apply(
        lambda value: valid_number(value, 1, 15)
    )
    frame["battery"] = frame["battery"].apply(
        lambda value: valid_number(value, 500, 50000)
    )
    frame["ram"] = frame["ram"].apply(lambda value: valid_number(value, 1, 64))
    frame["rom"] = frame["rom"].apply(lambda value: valid_number(value, 1, 4096))

    for column in [
        "resolution",
        "camera",
        "os",
        "release_date",
        "source",
        "url",
    ]:
        if column not in frame:
            frame[column] = ""
        frame[column] = frame[column].apply(clean_text)

    frame["url"] = frame["url"].str.slice(0, 255)

    if "core_count" not in frame:
        frame["core_count"] = ""
    frame["core_count"] = frame["core_count"].apply(clean_core_count)

    if "cpu" not in frame:
        frame["cpu"] = ""
    frame["cpu"] = frame["cpu"].apply(lambda value: clean_cpu(value)[:200])

    if "usage_scenes" not in frame:
        frame["usage_scenes"] = ""
    frame["usage_scenes"] = frame["usage_scenes"].apply(clean_usage_scenes)

    frame["camera"] = frame["camera"].replace({"暂无数据": ""})
    frame["source"] = frame["source"].replace({"": "ZOL"})
    frame["brand"] = frame["brand"].replace({"": "未知"})
    frame = frame[frame["price"].notna()]
    frame = frame.drop_duplicates(subset=["source_id", "url"], keep="first")
    frame = frame.sort_values("source_id")

    columns = [
        "source_id",
        "name",
        "brand",
        "price",
        "screen_size",
        "resolution",
        "battery",
        "core_count",
        "camera",
        "cpu",
        "ram",
        "rom",
        "os",
        "usage_scenes",
        "release_date",
        "source",
        "url",
    ]
    return frame[columns]


def ensure_database(host: str, port: int, user: str, password: str, database: str) -> None:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        charset="utf8mb4",
        autocommit=True,
    )
    with connection.cursor() as cursor:
        cursor.execute(
            (
                "CREATE DATABASE IF NOT EXISTS "
                f"`{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
    connection.close()


def write_to_mysql(
    frame: pd.DataFrame,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> int:
    ensure_database(host, port, user, password, database)
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        autocommit=True,
    )

    create_table_sql = SCHEMA.split("USE phone_recommender;", 1)[-1].strip()
    with connection.cursor() as cursor:
        cursor.execute(create_table_sql)

    insert_sql = """
    INSERT INTO phones_clean (
        source_id, name, brand, price, screen_size, resolution, battery,
        core_count, camera, cpu, ram, rom, os, usage_scenes, release_date,
        source, url
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        brand = VALUES(brand),
        price = VALUES(price),
        screen_size = VALUES(screen_size),
        resolution = VALUES(resolution),
        battery = VALUES(battery),
        core_count = VALUES(core_count),
        camera = VALUES(camera),
        cpu = VALUES(cpu),
        ram = VALUES(ram),
        rom = VALUES(rom),
        os = VALUES(os),
        usage_scenes = VALUES(usage_scenes),
        release_date = VALUES(release_date),
        source = VALUES(source),
        url = VALUES(url)
    """

    records = frame.astype(object).where(pd.notnull(frame), None).values.tolist()
    with connection.cursor() as cursor:
        cursor.executemany(insert_sql, records)
    connection.close()
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="清洗手机数据并写入 MySQL")
    parser.add_argument("--input", type=Path, default=Path("data/phones_raw.json"))
    parser.add_argument("--output-json", type=Path, default=Path("data/phones_clean.json"))
    parser.add_argument("--excel", type=Path, default=Path("data/phones_clean.xlsx"))
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

    if args.excel:
        args.excel.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_excel(args.excel, index=False)
        print(f"已导出 Excel：{args.excel}")


if __name__ == "__main__":
    main()
