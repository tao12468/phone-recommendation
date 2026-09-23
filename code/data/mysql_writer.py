"""把清洗后的手机数据写入 MySQL。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pymysql


SCHEMA = Path(__file__).with_name("schema_mysql.sql").read_text(encoding="utf-8")


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
    """将 DataFrame 写入 MySQL，重复运行时自动更新。"""

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
