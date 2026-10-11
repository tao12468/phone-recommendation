from algorithms.feedback_engine import update_preferences_from_phone


def test_update_preferences_from_phone():
    preferences = {
        "user_id": 1,
        "budget": None,
        "performance_score": 0.5,
        "brand_counts": {},
        "scene_counts": {},
        "os_counts": {},
    }
    phone = {
        "brand": "小米",
        "price": 4000,
        "performance_score": 0.9,
        "os_type": "安卓",
        "scene_game": 1,
        "scene_camera": 0,
    }
    updated = update_preferences_from_phone(preferences, phone, "favorite")
    assert updated["budget"] == 4000
    assert updated["brand_counts"]["小米"] == 5
    assert updated["scene_counts"]["游戏"] == 5
    assert updated["os_counts"]["安卓"] == 5
