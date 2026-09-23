"""阶段 1 的简单推荐逻辑。

当前版本只演示推荐系统的基本流程，后续会替换为：
内容过滤 + 协同过滤 + 知识图谱 + 动态混合策略。
"""


def _budget_match(phone_price: float, budget: float | None) -> float:
    if budget is None or budget <= 0:
        return 0.5

    diff = abs(phone_price - budget)
    scale = max(budget, phone_price, 1)
    return max(0.0, 1.0 - diff / scale)


def _brand_match(phone_brand: str, brands: list[str]) -> float:
    if not brands:
        return 0.5
    return 1.0 if phone_brand in brands else 0.0


def _scene_match(phone_scenes: list[str], scenes: list[str]) -> float:
    if not scenes:
        return 0.5

    phone_set = set(phone_scenes)
    scene_set = set(scenes)
    overlap = len(phone_set & scene_set)
    return overlap / max(len(scene_set), 1)


def recommend(phones: list[dict], preferences: dict | None = None, limit: int = 5) -> list[dict]:
    """返回推荐结果。

    有偏好时，按预算、品牌、使用场景和性价比综合打分；
    没有偏好时，退化为热门推荐，解决冷启动问题。
    """

    preferences = preferences or {}
    budget = preferences.get("budget")
    brands = preferences.get("brands") or []
    scenes = preferences.get("scenes") or []

    if not budget and not brands and not scenes:
        scored = []
        for phone in phones:
            score = phone["popularity"] * 0.6 + phone["value_score"] * 10 * 0.4
            scored.append(
                {
                    "phone": phone,
                    "score": round(score, 2),
                    "reason": "热门机型 + 高性价比",
                }
            )
    else:
        weights = {"budget": 0.35, "brand": 0.25, "scene": 0.25, "value": 0.15}
        scored = []
        for phone in phones:
            budget_score = _budget_match(phone["price"], budget)
            brand_score = _brand_match(phone["brand"], brands)
            scene_score = _scene_match(phone["scenes"], scenes)
            value_score = phone["value_score"] / 10.0
            score = (
                budget_score * weights["budget"]
                + brand_score * weights["brand"]
                + scene_score * weights["scene"]
                + value_score * weights["value"]
            )

            reasons = []
            if budget_score >= 0.85:
                reasons.append("预算匹配")
            if brand_score >= 0.85:
                reasons.append("品牌符合")
            if scene_score >= 0.85:
                reasons.append("场景符合")
            if value_score >= 0.85:
                reasons.append("性价比高")
            if not reasons:
                reasons.append("综合表现较好")

            scored.append(
                {
                    "phone": phone,
                    "score": round(score, 4),
                    "reason": "、".join(reasons),
                }
            )

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]
