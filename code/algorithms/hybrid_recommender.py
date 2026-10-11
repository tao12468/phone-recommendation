"""混合推荐策略：融合内容过滤与协同过滤。"""

from __future__ import annotations

import pandas as pd

from algorithms import collaborative_recommender, content_recommender


def _normalize(items: list[dict], key: str) -> dict[int, float]:
    """把每个推荐列表的分数归一化到 0 到 1。"""

    result: dict[int, float] = {}
    if not items:
        return result

    values = [item[key] for item in items]
    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return {item["source_id"]: 1.0 for item in items}

    for item in items:
        result[item["source_id"]] = (item[key] - minimum) / (maximum - minimum)
    return result


def recommend_hybrid(
    preferences: dict | None = None,
    user_id: int | None = None,
    top_n: int = 5,
    interactions: pd.DataFrame | None = None,
    phones: pd.DataFrame | None = None,
) -> list[dict]:
    """融合内容过滤与协同过滤，返回最终推荐。"""

    preferences = preferences or {}
    phones = phones if phones is not None else content_recommender.load_phones()

    content_items = content_recommender.recommend(
        preferences,
        top_n=max(top_n * 2, 10),
        phones=phones,
    )

    collaborative_items = []
    if interactions is not None and user_id is not None:
        collaborative_items = collaborative_recommender.recommend_for_user(
            user_id,
            top_n=max(top_n * 2, 10),
            interactions=interactions,
            phones=phones,
        )

    content_norm = _normalize(content_items, "score")
    collaborative_norm = _normalize(collaborative_items, "predicted_score")

    if collaborative_items:
        weight_content = 0.55
        weight_collaborative = 0.45
    else:
        weight_content = 1.0
        weight_collaborative = 0.0

    merged: dict[int, dict] = {}
    for item in content_items:
        source_id = item["source_id"]
        merged[source_id] = {
            "source_id": source_id,
            "name": item["name"],
            "brand": item["brand"],
            "price": item["price"],
            "position": item.get("position", ""),
            "price_level": item.get("price_level", ""),
            "content_score": round(item["score"], 4),
            "collaborative_score": None,
            "reason": item.get("reason", ""),
        }

    for item in collaborative_items:
        source_id = item["source_id"]
        if source_id not in merged:
            merged[source_id] = {
                "source_id": source_id,
                "name": item["name"],
                "brand": item["brand"],
                "price": item["price"],
                "position": "",
                "price_level": "",
                "content_score": None,
                "collaborative_score": round(item["predicted_score"], 4),
                "reason": item.get("reason", ""),
            }
        else:
            merged[source_id]["collaborative_score"] = round(
                item["predicted_score"], 4
            )

    ranked = []
    for source_id, item in merged.items():
        score = (
            weight_content * content_norm.get(source_id, 0.0)
            + weight_collaborative * collaborative_norm.get(source_id, 0.0)
        )
        item["score"] = round(score, 4)
        if item["collaborative_score"] is not None and item["content_score"] is not None:
            item["reason"] = "内容过滤 + 协同过滤"
        elif item["collaborative_score"] is None:
            item["reason"] = "内容过滤"
        else:
            item["reason"] = "协同过滤"
        ranked.append(item)

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_n]
