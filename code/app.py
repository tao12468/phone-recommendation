"""基于数据驱动的个性化手机推荐平台。

阶段 1：最小可运行闭环。
"""

from flask import Flask, jsonify, request, send_from_directory

from algorithms.simple_recommender import recommend
from data.sample_phones import PHONES


app = Flask(__name__, static_folder="static", static_url_path="/static")


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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
