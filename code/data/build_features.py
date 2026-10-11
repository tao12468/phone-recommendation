"""从 MySQL 读取清洗后的数据，生成特征并写回 MySQL。"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pymysql

from algorithms.feature_engineering import build_features
from data.mysql_writer import ensure_database


FEATURE_COLUMNS = [
    "source_id",
    "name",
    "brand",
    "brand_id",
    "price",
    "screen_size",
    "battery",
    "ram",
    "rom",
    "price_level",
    "position",
    "performance_score",
    "value_for_money",
    "os_type",
    "core_count_num",
    "resolution_width",
    "resolution_height",
    "release_year",
    "scene_game",
    "scene_camera",
    "scene_music",
    "scene_business",
    "scene_selfie",
    "scene_fastcharge",
    "scene_5g",
    "scene_fold",
    "scene_bigscreen",
    "scene_elderly",
    "scene_rugged",
]

CREATE_FEATURES_TABLE = """
CREATE TABLE IF NOT EXISTS phones_features (
    source_id BIGINT NOT NULL,
    name VARCHAR(255),
    brand VARCHAR(64),
    brand_id INT,
    price DECIMAL(10, 2),
    screen_size DECIMAL(6, 2),
    battery DECIMAL(10, 1),
    ram DECIMAL(6, 1),
    rom DECIMAL(10, 1),
    price_level VARCHAR(20),
    position VARCHAR(20),
    performance_score DECIMAL(5, 3),
    value_for_money DECIMAL(8, 5),
    os_type VARCHAR(20),
    core_count_num INT,
    resolution_width INT,
    resolution_height INT,
    release_year INT,
    scene_game TINYINT,
    scene_camera TINYINT,
    scene_music TINYINT,
    scene_business TINYINT,
    scene_selfie TINYINT,
    scene_fastcharge TINYINT,
    scene_5g TINYINT,
    scene_fold TINYINT,
    scene_bigscreen TINYINT,
    scene_elderly TINYINT,
    scene_rugged TINYINT,
    PRIMARY KEY (source_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


def read_clean_phones(
    host: str, port: int, user: str, password: str, database: str
) -> pd.DataFrame:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM phones_clean")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
    connection.close()
    return pd.DataFrame(rows, columns=columns)


def write_features_to_mysql(
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
    with connection.cursor() as cursor:
        cursor.execute(CREATE_FEATURES_TABLE)

    column_list = ", ".join(FEATURE_COLUMNS)
    placeholders = ", ".join(["%s"] * len(FEATURE_COLUMNS))
    update_list = ", ".join(
        f"{column} = VALUES({column})" for column in FEATURE_COLUMNS if column != "source_id"
    )
    insert_sql = (
        f"INSERT INTO phones_features ({column_list}) VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {update_list}"
    )

    records = (
        frame[FEATURE_COLUMNS]
        .astype(object)
        .where(pd.notnull(frame[FEATURE_COLUMNS]), None)
        .values.tolist()
    )
    with connection.cursor() as cursor:
        cursor.executemany(insert_sql, records)
    connection.close()
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="生成手机特征并写入 MySQL")
    parser.add_argument("--output-json", type=Path, default=Path("data/phones_features.json"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default="phone_recommender")
    parser.add_argument("--skip-db", action="store_true", help="只生成特征，不写入 MySQL")
    args = parser.parse_args()

    clean_frame = read_clean_phones(
        args.host, args.port, args.user, args.password, args.database
    )
    features = build_features(clean_frame)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    features.to_json(args.output_json, orient="records", force_ascii=False, indent=2)

    if not args.skip_db:
        count = write_features_to_mysql(
            features,
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database,
        )
        print(f"已生成并写入 MySQL：{count} 条特征")
    else:
        print(f"已生成特征：{len(features)} 条，未写入 MySQL")


if __name__ == "__main__":
    main()
