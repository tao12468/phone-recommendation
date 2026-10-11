"""基于数据驱动的个性化手机推荐平台。

阶段 1：最小可运行闭环。
"""

import os

from flask import Flask, jsonify, request, send_from_directory

from algorithms import content_recommender
from algorithms import collaborative_recommender
from algorithms.simple_recommender import recommend
from data import database
from data import interaction_repository
from data.sample_phones import PHONES


app = Flask(__name__, static_folder="static", static_url_path="/static")

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


@app.get("/api/phones/similar/<int:phone_id>")
def similar_phone_list(phone_id: int):
    limit = request.args.get("limit", 5, type=int)
    limit = max(1, min(limit, 10))
    items = content_recommender.similar_phones(phone_id, top_n=limit)
    return jsonify({"items": items})


@app.get("/data")
def data_viewer():
    return send_from_directory("static", "data_viewer.html")


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
