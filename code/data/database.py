"""手机推荐系统的数据访问层。

当前阶段使用 SQLite，方便本地查看和快速开发。
后续可以将 SQLite 替换为 MySQL，调用方式保持不变。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("phone_recommender.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS phones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    brand TEXT DEFAULT '',
    price REAL,
    screen_size REAL,
    resolution TEXT DEFAULT '',
    battery REAL,
    core_count TEXT DEFAULT '',
    camera TEXT DEFAULT '',
    cpu TEXT DEFAULT '',
    ram REAL,
    rom REAL,
    os TEXT DEFAULT '',
    usage_scenes TEXT DEFAULT '',
    release_date TEXT DEFAULT '',
    source TEXT DEFAULT 'ZOL',
    url TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    """创建数据库连接。"""

    target = db_path or DB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: Path | None = None) -> None:
    """创建手机表。"""

    with connect(db_path) as connection:
        connection.executescript(SCHEMA)


def import_phones(records: list[dict], db_path: Path | None = None) -> int:
    """将手机数据写入数据库。

    使用 source_id 作为唯一标识，重复运行时自动覆盖更新。
    """

    init_db(db_path)
    insert_sql = """
    INSERT OR REPLACE INTO phones (
        source_id, name, brand, price, screen_size, resolution, battery,
        core_count, camera, cpu, ram, rom, os, usage_scenes, release_date,
        source, url
    ) VALUES (
        :id, :name, :brand, :price, :screen_size, :resolution, :battery,
        :core_count, :camera, :cpu, :ram, :rom, :os, :usage_scenes, :release_date,
        :source, :url
    )
    """

    with connect(db_path) as connection:
        connection.executemany(insert_sql, records)
    return len(records)


def count_phones(db_path: Path | None = None) -> int:
    """统计手机数据条数。"""

    init_db(db_path)
    with connect(db_path) as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM phones").fetchone()
        return int(row["total"])


def get_phones_page(
    page: int = 1,
    page_size: int = 20,
    brand: str | None = None,
    keyword: str | None = None,
    db_path: Path | None = None,
) -> dict:
    """分页查询手机数据。"""

    init_db(db_path)
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    where_parts: list[str] = []
    params: dict = {}

    if brand:
        where_parts.append("brand = :brand")
        params["brand"] = brand
    if keyword:
        where_parts.append("(name LIKE :keyword OR cpu LIKE :keyword)")
        params["keyword"] = f"%{keyword}%"

    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
    total_sql = f"SELECT COUNT(*) AS total FROM phones {where_sql}"
    list_sql = f"""
        SELECT * FROM phones
        {where_sql}
        ORDER BY id DESC
        LIMIT :limit OFFSET :offset
    """

    with connect(db_path) as connection:
        total = int(
            connection.execute(total_sql, params).fetchone()["total"]
        )
        query_params = dict(params)
        query_params["limit"] = page_size
        query_params["offset"] = (page - 1) * page_size
        rows = connection.execute(list_sql, query_params).fetchall()
        items = [dict(row) for row in rows]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


def get_brands(db_path: Path | None = None) -> list[str]:
    """返回数据库中已有的品牌。"""

    init_db(db_path)
    with connect(db_path) as connection:
        rows = connection.execute(
            "SELECT DISTINCT brand FROM phones WHERE brand != '' ORDER BY brand"
        ).fetchall()
        return [str(row["brand"]) for row in rows]
