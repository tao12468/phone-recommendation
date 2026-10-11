import pandas as pd

from algorithms.hybrid_recommender import recommend_hybrid


def test_hybrid_cold_start():
    phones = pd.DataFrame(
        [
            {"source_id": 1001, "name": "手机A", "brand": "小米", "price": 3000, "position": "中端", "price_level": "中端", "performance_score": 0.7, "value_for_money": 0.6, "os_type": "安卓"},
            {"source_id": 1002, "name": "手机B", "brand": "华为", "price": 4000, "position": "中端", "price_level": "中端", "performance_score": 0.8, "value_for_money": 0.5, "os_type": "安卓"},
            {"source_id": 1003, "name": "手机C", "brand": "vivo", "price": 3500, "position": "中端", "price_level": "中端", "performance_score": 0.75, "value_for_money": 0.55, "os_type": "安卓"},
        ]
    )
    items = recommend_hybrid(
        preferences={"budget": 3500},
        user_id=1,
        top_n=3,
        interactions=pd.DataFrame(),
        phones=phones,
    )
    assert len(items) == 3
    assert all(item["reason"] == "内容过滤" for item in items)


def test_hybrid_merges_sources():
    phones = pd.DataFrame(
        [
            {"source_id": 1001, "name": "手机A", "brand": "小米", "price": 3000, "position": "中端", "price_level": "中端", "performance_score": 0.7, "value_for_money": 0.6, "os_type": "安卓"},
            {"source_id": 1002, "name": "手机B", "brand": "华为", "price": 4000, "position": "中端", "price_level": "中端", "performance_score": 0.8, "value_for_money": 0.5, "os_type": "安卓"},
            {"source_id": 1003, "name": "手机C", "brand": "vivo", "price": 3500, "position": "中端", "price_level": "中端", "performance_score": 0.75, "value_for_money": 0.55, "os_type": "安卓"},
        ]
    )
    interactions = pd.DataFrame(
        [
            {"user_id": 1, "phone_source_id": 1001, "weight": 5},
            {"user_id": 2, "phone_source_id": 1001, "weight": 5},
            {"user_id": 2, "phone_source_id": 1003, "weight": 5},
        ]
    )
    items = recommend_hybrid(
        preferences={"budget": 3500},
        user_id=1,
        top_n=3,
        interactions=interactions,
        phones=phones,
    )
    assert len(items) == 3
