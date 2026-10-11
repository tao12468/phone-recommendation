"""用户注册、登录与查询。"""

from __future__ import annotations

import bcrypt
import pymysql

from data.mysql_writer import ensure_database


CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


def ensure_users_table(
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
        cursor.execute(CREATE_USERS_TABLE)
    connection.close()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def register_user(
    username: str,
    password: str,
    host: str,
    port: int,
    user: str,
    db_password: str,
    database: str,
) -> dict:
    ensure_users_table(host, port, user, db_password, database)
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=db_password,
        database=database,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hash_password(password)),
            )
        user_id = connection.insert_id()
    except pymysql.err.IntegrityError as exc:
        raise ValueError("用户名已存在") from exc
    finally:
        connection.close()
    return {"id": user_id, "username": username}


def get_user_by_username(
    username: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> dict | None:
    ensure_users_table(host, port, user, password, database)
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
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,),
        )
        row = cursor.fetchone()
    connection.close()
    if row is None:
        return None
    return {"id": row[0], "username": row[1], "password_hash": row[2]}


def get_user_by_id(
    user_id: int,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> dict | None:
    ensure_users_table(host, port, user, password, database)
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
            "SELECT id, username FROM users WHERE id = %s",
            (user_id,),
        )
        row = cursor.fetchone()
    connection.close()
    if row is None:
        return None
    return {"id": row[0], "username": row[1]}
