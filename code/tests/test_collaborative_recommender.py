import pandas as pd

from algorithms.collaborative_recommender import recommend_for_user


def sample_interactions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"user_id": 1, "phone_source_id": 1001, "event_type": "favorite", "weight": 5},
            {"user_id": 1, "phone_source_id": 1002, "event_type": "click", "weight": 2},
            {"user_id": 2, "phone_source_id": 1001, "event_type": "favorite", "weight": 5},
            {"user_id": 2, "phone_source_id": 1003, "event_type": "favorite", "weight": 5},
            {"user_id": 3, "phone_source_id": 1002, "event_type": "favorite", "weight": 5},
            {"user_id": 3, "phone_source_id": 1003, "event_type": "favorite", "weight": 5},
        ]
    )


def test_build_and_recommend():
    phones = pd.DataFrame(
        [
            {"source_id": 1001, "name": "手机A", "brand": "小米", "price": 3000},
            {"source_id": 1002, "name": "手机B", "brand": "华为", "price": 4000},
            {"source_id": 1003, "name": "手机C", "brand": "vivo", "price": 3500},
        ]
    )
    items = recommend_for_user(
        user_id=1,
        top_n=2,
        interactions=sample_interactions(),
        phones=phones,
    )
    assert len(items) == 1
    assert items[0]["source_id"] == 1003
