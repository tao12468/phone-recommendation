"""基于数据驱动的个性化手机推荐平台。

阶段 1：最小可运行闭环。
"""

import json
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from auth_utils import create_token, user_id_from_authorization
from algorithms import content_recommender
from algorithms import collaborative_recommender
from algorithms import feedback_engine
from algorithms import hybrid_recommender
from algorithms.simple_recommender import recommend
from data import database
from data import interaction_repository
from data import preference_repository
from data import user_repository
from data.sample_phones import PHONES


app = Flask(__name__, static_folder="static", static_url_path="/static")

PHONE_IMAGES_PATH = Path(__file__).resolve().parent / "data" / "phone_images.json"

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "123456"),
    "database": os.environ.get("MYSQL_DATABASE", "phone_recommender"),
}


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "stage": 1,
            "message": "最小可运行闭环已启动",
        }
    )


@app.get("/api/phone-images")
def phone_images():
    image_map = json.loads(PHONE_IMAGES_PATH.read_text(encoding="utf-8"))
    return jsonify(image_map)


@app.post("/api/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    try:
        db_config = {**MYSQL_CONFIG, "db_password": MYSQL_CONFIG["password"]}
        db_config.pop("password", None)
        user = user_repository.register_user(username, password, **db_config)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409

    return jsonify({"token": create_token(user["id"]), "user": user})


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    user = user_repository.get_user_by_username(username, **MYSQL_CONFIG)
    if user is None or not user_repository.verify_password(
        password, user["password_hash"]
    ):
        return jsonify({"error": "用户名或密码错误"}), 401

    return jsonify(
        {
            "token": create_token(user["id"]),
            "user": {"id": user["id"], "username": user["username"]},
        }
    )


@app.get("/api/auth/me")
def auth_me():
    user_id = user_id_from_authorization(request.headers.get("Authorization"))
    if user_id is None:
        return jsonify({"error": "未登录或令牌无效"}), 401

    user = user_repository.get_user_by_id(user_id, **MYSQL_CONFIG)
    if user is None:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify(user)


@app.get("/api/phones")
def phones():
    brand = request.args.get("brand")
    scene = request.args.get("scene")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort = request.args.get("sort", "popularity")

    result = list(PHONES)

    if brand:
        result = [phone for phone in result if phone["brand"] == brand]
    if scene:
        result = [phone for phone in result if scene in phone["scenes"]]
    if min_price is not None:
        result = [phone for phone in result if phone["price"] >= min_price]
    if max_price is not None:
        result = [phone for phone in result if phone["price"] <= max_price]

    sort_options = {
        "popularity": lambda phone: phone["popularity"],
        "value": lambda phone: phone["value_score"],
        "price_asc": lambda phone: -phone["price"],
        "price_desc": lambda phone: phone["price"],
    }
    if sort in sort_options:
        result.sort(key=sort_options[sort], reverse=sort in {"popularity", "value"})

    return jsonify({"total": len(result), "items": result})


@app.get("/api/phones/<int:phone_id>")
def phone_detail(phone_id: int):
    phone = next((item for item in PHONES if item["id"] == phone_id), None)
    if phone is None:
        return jsonify({"error": "未找到该手机"}), 404
    return jsonify(phone)


@app.get("/api/recommendations")
def recommendations():
    budget = request.args.get("budget", type=float)
    brands = _split_csv(request.args.get("brand"))
    scenes = _split_csv(request.args.get("scene"))
    limit = request.args.get("limit", 5, type=int)
    limit = max(1, min(limit, 10))

    preferences = {
        "budget": budget,
        "brands": brands,
        "scenes": scenes,
    }
    items = recommend(PHONES, preferences, limit=limit)

    return jsonify(
        {
            "items": items,
            "strategy": "simple_content_based",
            "message": "阶段 1 简单推荐",
        }
    )


@app.get("/api/recommendations/content")
def content_recommendations():
    budget = request.args.get("budget", type=float)
    brands = _split_csv(request.args.get("brand"))
    scenes = _split_csv(request.args.get("scene"))
    preferred_os = _split_csv(request.args.get("os"))
    limit = request.args.get("limit", 5, type=int)
    limit = max(1, min(limit, 10))

    preferences = {
        "budget": budget,
        "brands": brands,
        "scenes": scenes,
        "os": preferred_os,
    }
    items = content_recommender.recommend(preferences, top_n=limit)

    return jsonify(
        {
            "items": items,
            "strategy": "content_based",
            "message": "基于内容过滤推荐",
        }
    )


@app.get("/api/recommendations/collaborative")
def collaborative_recommendations():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "缺少 user_id 参数"}), 400
    limit = request.args.get("limit", 5, type=int)
    limit = max(1, min(limit, 10))

    interactions = interaction_repository.load_interactions(**MYSQL_CONFIG)
    items = collaborative_recommender.recommend_for_user(
        user_id,
        top_n=limit,
        interactions=interactions,
    )
    message = (
        "协同过滤推荐"
        if items
        else "该用户暂无足够交互数据，可先用冷启动或内容过滤"
    )
    return jsonify(
        {
            "items": items,
            "strategy": "collaborative",
            "message": message,
        }
    )


@app.get("/api/recommendations/hybrid")
def hybrid_recommendations():
    auth_user_id = user_id_from_authorization(request.headers.get("Authorization"))
    user_id = auth_user_id or request.args.get("user_id", type=int)
    budget = request.args.get("budget", type=float)
    brands = _split_csv(request.args.get("brand"))
    scenes = _split_csv(request.args.get("scene"))
    preferred_os = _split_csv(request.args.get("os"))
    limit = request.args.get("limit", 5, type=int)
    limit = max(1, min(limit, 10))

    preferences = {
        "budget": budget,
        "brands": brands,
        "scenes": scenes,
        "os": preferred_os,
    }
    interactions = (
        interaction_repository.load_interactions(**MYSQL_CONFIG)
        if user_id
        else None
    )
    items = hybrid_recommender.recommend_hybrid(
        preferences,
        user_id=user_id,
        top_n=limit,
        interactions=interactions,
    )
    return jsonify(
        {
            "items": items,
            "strategy": "hybrid",
            "message": "内容过滤与协同过滤的混合推荐",
        }
    )


@app.get("/api/phones/similar/<int:phone_id>")
def similar_phone_list(phone_id: int):
    limit = request.args.get("limit", 5, type=int)
    limit = max(1, min(limit, 10))
    items = content_recommender.similar_phones(phone_id, top_n=limit)
    return jsonify({"items": items})


@app.post("/api/behavior")
def record_behavior():
    payload = request.get_json(silent=True) or request.form
    auth_user_id = user_id_from_authorization(request.headers.get("Authorization"))
    user_id = auth_user_id or payload.get("user_id")
    phone_source_id = payload.get("phone_source_id")
    event_type = payload.get("event_type")

    try:
        user_id = int(user_id)
        phone_source_id = int(phone_source_id)
    except (TypeError, ValueError):
        user_id = None
        phone_source_id = None

    if not user_id or not phone_source_id or event_type not in {"view", "click", "compare", "favorite"}:
        return jsonify({"error": "参数不完整或 event_type 不合法"}), 400

    preferences = feedback_engine.record_interaction(
        user_id,
        phone_source_id,
        event_type,
        MYSQL_CONFIG,
    )
    return jsonify({"status": "ok", "preferences": preferences})


@app.get("/api/preferences/<int:user_id>")
def user_preferences(user_id: int):
    preferences = preference_repository.load_preferences(user_id, **MYSQL_CONFIG)
    return jsonify(preferences)


@app.get("/api/me/preferences")
def my_preferences():
    user_id = user_id_from_authorization(request.headers.get("Authorization"))
    if user_id is None:
        return jsonify({"error": "未登录或令牌无效"}), 401
    preferences = preference_repository.load_preferences(user_id, **MYSQL_CONFIG)
    return jsonify(preferences)


@app.get("/data")
def data_viewer():
    return send_from_directory("static", "data_viewer.html")


@app.get("/demo")
def demo_page():
    return send_from_directory("static", "demo.html")


@app.get("/app")
def app_page():
    return send_from_directory("static", "app.html")


@app.get("/api/db/phones")
def database_phones():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    brand = request.args.get("brand")
    keyword = request.args.get("keyword")
    result = database.get_phones_page(
        page=page,
        page_size=page_size,
        brand=brand,
        keyword=keyword,
    )
    return jsonify(result)


@app.get("/api/db/brands")
def database_brands():
    return jsonify({"items": database.get_brands()})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
