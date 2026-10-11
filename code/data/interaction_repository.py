"""用户-手机交互数据的存储与读取。"""

from __future__ import annotations

import pandas as pd
import pymysql

from data.mysql_writer import ensure_database


CREATE_INTERACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS user_interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    phone_source_id BIGINT NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    weight INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_phone_event (user_id, phone_source_id, event_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

EVENT_WEIGHTS = {
    "view": 1,
    "click": 2,
    "compare": 3,
    "favorite": 5,
}


def ensure_interactions_table(
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
        cursor.execute(CREATE_INTERACTIONS_TABLE)
    connection.close()


def insert_interactions(
    records: list[dict],
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> int:
    ensure_interactions_table(host, port, user, password, database)
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
    INSERT INTO user_interactions (user_id, phone_source_id, event_type, weight)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE weight = VALUES(weight)
    """
    rows = [
        (
            int(record["user_id"]),
            int(record["phone_source_id"]),
            record["event_type"],
            int(EVENT_WEIGHTS.get(record["event_type"], 1)),
        )
        for record in records
    ]
    with connection.cursor() as cursor:
        cursor.executemany(insert_sql, rows)
    connection.close()
    return len(rows)


def load_interactions(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> pd.DataFrame:
    ensure_interactions_table(host, port, user, password, database)
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
            "SELECT user_id, phone_source_id, event_type, weight "
            "FROM user_interactions"
        )
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
    connection.close()
    return pd.DataFrame(rows, columns=columns)
