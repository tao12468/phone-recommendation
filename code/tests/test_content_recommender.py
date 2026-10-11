from algorithms import content_recommender


def test_recommend_with_preferences():
    items = content_recommender.recommend(
        preferences={
            "budget": 4000,
            "brands": ["小米", "vivo"],
            "scenes": ["游戏", "拍照"],
            "os": ["安卓"],
        },
        top_n=5,
    )
    assert len(items) == 5
    assert items[0]["score"] >= items[-1]["score"]
    assert "score" in items[0]


def test_recommend_cold_start():
    items = content_recommender.recommend(preferences={}, top_n=5)
    assert len(items) == 5


def test_similar_phones():
    phones = content_recommender.load_phones()
    source_id = int(phones.iloc[0]["source_id"])
    items = content_recommender.similar_phones(source_id, top_n=3)
    assert len(items) == 3
    assert all(item["source_id"] != source_id for item in items)
