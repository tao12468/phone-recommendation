"""用户偏好向量的存储与读取。"""

from __future__ import annotations

import json

import pymysql

from data.mysql_writer import ensure_database


CREATE_PREFERENCES_TABLE = """
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id INT PRIMARY KEY,
    budget DOUBLE DEFAULT NULL,
    performance_score DOUBLE DEFAULT 0.5,
    brand_counts TEXT,
    scene_counts TEXT,
    os_counts TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


def default_preferences(user_id: int) -> dict:
    return {
        "user_id": user_id,
        "budget": None,
        "performance_score": 0.5,
        "brand_counts": {},
        "scene_counts": {},
        "os_counts": {},
    }


def ensure_preferences_table(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> None:
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
        cursor.execute(CREATE_PREFERENCES_TABLE)
    connection.close()


def load_preferences(
    user_id: int,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> dict:
    ensure_preferences_table(host, port, user, password, database)
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
    )
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, budget, performance_score, brand_counts, "
            "scene_counts, os_counts FROM user_preferences WHERE user_id = %s",
            (user_id,),
        )
        row = cursor.fetchone()
    connection.close()

    if row is None:
        return default_preferences(user_id)

    return {
        "user_id": int(row[0]),
        "budget": float(row[1]) if row[1] is not None else None,
        "performance_score": float(row[2]),
        "brand_counts": json.loads(row[3]),
        "scene_counts": json.loads(row[4]),
        "os_counts": json.loads(row[5]),
    }


def save_preferences(
    preferences: dict,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> None:
    ensure_preferences_table(host, port, user, password, database)
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        autocommit=True,
    )
    insert_sql = """
    INSERT INTO user_preferences
        (user_id, budget, performance_score, brand_counts, scene_counts, os_counts)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        budget = VALUES(budget),
        performance_score = VALUES(performance_score),
        brand_counts = VALUES(brand_counts),
        scene_counts = VALUES(scene_counts),
        os_counts = VALUES(os_counts)
    """
    with connection.cursor() as cursor:
        cursor.execute(
            insert_sql,
            (
                int(preferences["user_id"]),
                preferences.get("budget"),
                float(preferences.get("performance_score", 0.5)),
                json.dumps(preferences.get("brand_counts", {}), ensure_ascii=False),
                json.dumps(preferences.get("scene_counts", {}), ensure_ascii=False),
                json.dumps(preferences.get("os_counts", {}), ensure_ascii=False),
            ),
        )
    connection.close()
