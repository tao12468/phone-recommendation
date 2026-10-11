"""行为反馈与偏好动态更新。"""

from __future__ import annotations

from algorithms.content_recommender import SCENE_TO_COLUMN, load_phones
from data import preference_repository
from data.interaction_repository import EVENT_WEIGHTS, insert_interactions


def update_preferences_from_phone(
    preferences: dict,
    phone: dict,
    event_type: str,
) -> dict:
    """根据用户对某款手机的行为更新偏好向量。"""

    weight = EVENT_WEIGHTS.get(event_type, 1)
    alpha = min(0.35, 0.05 + 0.05 * weight)

    price = float(phone["price"])
    if preferences.get("budget") is None:
        preferences["budget"] = price
    else:
        preferences["budget"] = (
            preferences["budget"] * (1 - alpha) + price * alpha
        )

    phone_performance = float(phone.get("performance_score", 0.5))
    preferences["performance_score"] = (
        preferences.get("performance_score", 0.5) * (1 - alpha)
        + phone_performance * alpha
    )

    brand = phone["brand"]
    brand_counts = preferences.setdefault("brand_counts", {})
    brand_counts[brand] = brand_counts.get(brand, 0) + weight

    os_type = phone.get("os_type", "")
    os_counts = preferences.setdefault("os_counts", {})
    if os_type:
        os_counts[os_type] = os_counts.get(os_type, 0) + weight

    scene_counts = preferences.setdefault("scene_counts", {})
    for scene, column in SCENE_TO_COLUMN.items():
        if phone.get(column) == 1:
            scene_counts[scene] = scene_counts.get(scene, 0) + weight

    return preferences


def record_interaction(
    user_id: int,
    phone_source_id: int,
    event_type: str,
    db_config: dict,
) -> dict:
    """记录交互并更新用户偏好。"""

    insert_interactions(
        [{"user_id": user_id, "phone_source_id": phone_source_id, "event_type": event_type}],
        **db_config,
    )

    phones = load_phones()
    matched = phones[phones["source_id"] == int(phone_source_id)]
    if matched.empty:
        return preference_repository.load_preferences(user_id, **db_config)

    phone = matched.iloc[0].to_dict()
    preferences = preference_repository.load_preferences(user_id, **db_config)
    preferences = update_preferences_from_phone(preferences, phone, event_type)
    preference_repository.save_preferences(preferences, **db_config)
    return preferences
