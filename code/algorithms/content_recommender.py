"""基于内容过滤的手机推荐算法。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


FEATURES_PATH = Path(__file__).resolve().parents[1] / "data" / "phones_features.json"

SCENE_TO_COLUMN = {
    "游戏": "scene_game",
    "拍照": "scene_camera",
    "音乐": "scene_music",
    "商务": "scene_business",
    "自拍": "scene_selfie",
    "快充": "scene_fastcharge",
    "5G": "scene_5g",
    "折叠屏": "scene_fold",
    "大屏": "scene_bigscreen",
    "老人机": "scene_elderly",
    "三防": "scene_rugged",
}

SCENE_COLUMNS = list(SCENE_TO_COLUMN.values())

NUMERIC_COLUMNS = [
    "price",
    "screen_size",
    "battery",
    "ram",
    "rom",
    "performance_score",
    "value_for_money",
    "core_count_num",
    "resolution_width",
    "resolution_height",
    "release_year",
]


def load_phones(path: Path = FEATURES_PATH) -> pd.DataFrame:
    """加载手机特征数据。"""

    frame = pd.read_json(path)
    for column in SCENE_COLUMNS:
        if column not in frame:
            frame[column] = 0
        frame[column] = frame[column].fillna(0).astype(int)
    return frame


def budget_score(price: float, budget: float | None) -> float:
    if not budget or budget <= 0:
        return 0.5
    diff = abs(price - budget)
    scale = max(price, budget, 1)
    return float(max(0.0, 1.0 - diff / scale))


def scene_overlap(row: pd.Series, scenes: list[str]) -> float:
    matched = 0
    for scene in scenes:
        column = SCENE_TO_COLUMN.get(scene)
        if column and row.get(column) == 1:
            matched += 1
    return matched / max(len(scenes), 1)


def os_score(row: pd.Series, preferred_os: list[str]) -> float:
    if not preferred_os:
        return 0.5
    return 1.0 if row.get("os_type") in preferred_os else 0.0


def build_reason(
    budget_s: float,
    brand_s: float,
    scene_s: float,
    os_s: float,
    perf_value: float,
) -> str:
    reasons = []
    if budget_s >= 0.85:
        reasons.append("预算匹配")
    if brand_s >= 0.85:
        reasons.append("品牌符合")
    if scene_s >= 0.85:
        reasons.append("场景符合")
    if os_s >= 0.85:
        reasons.append("系统符合")
    if perf_value >= 0.6:
        reasons.append("性能与性价比均衡")
    return "、".join(reasons) if reasons else "综合匹配"


def recommend(
    preferences: dict | None = None,
    top_n: int = 5,
    phones: pd.DataFrame | None = None,
) -> list[dict]:
    """根据用户偏好返回手机推荐列表。"""

    preferences = preferences or {}
    phones = phones if phones is not None else load_phones()
    budget = preferences.get("budget")
    brands = preferences.get("brands") or []
    scenes = preferences.get("scenes") or []
    preferred_os = preferences.get("os") or []

    rows = []
    for _, row in phones.iterrows():
        budget_s = budget_score(row["price"], budget)
        brand_s = 1.0 if not brands else (1.0 if row["brand"] in brands else 0.0)
        scene_s = scene_overlap(row, scenes) if scenes else 0.5
        os_s = os_score(row, preferred_os) if preferred_os else 0.5
        perf_value = (row["performance_score"] + row["value_for_money"]) / 2

        score = (
            budget_s * 0.30
            + brand_s * 0.15
            + scene_s * 0.25
            + os_s * 0.10
            + perf_value * 0.20
        )
        rows.append(
            {
                "source_id": int(row["source_id"]),
                "name": row["name"],
                "brand": row["brand"],
                "price": float(row["price"]),
                "position": row.get("position", ""),
                "price_level": row.get("price_level", ""),
                "score": round(float(score), 4),
                "reason": build_reason(budget_s, brand_s, scene_s, os_s, perf_value),
            }
        )

    rows.sort(key=lambda item: item["score"], reverse=True)
    return rows[:top_n]


def phone_vector_matrix(phones: pd.DataFrame) -> np.ndarray:
    """构建手机特征矩阵，用于相似度计算。"""

    numeric = phones[NUMERIC_COLUMNS].fillna(phones[NUMERIC_COLUMNS].median())
    scaled = StandardScaler().fit_transform(numeric)
    scene_flags = phones[SCENE_COLUMNS].to_numpy(dtype=float)
    os_flags = pd.get_dummies(phones["os_type"], prefix="os").to_numpy(dtype=float)
    return np.hstack([scaled, scene_flags, os_flags])


def similar_phones(
    source_id: int,
    top_n: int = 5,
    phones: pd.DataFrame | None = None,
) -> list[dict]:
    """返回与指定手机最相似的其他手机。"""

    phones = phones if phones is not None else load_phones()
    matrix = phone_vector_matrix(phones)
    similarities = cosine_similarity(matrix)

    indices = phones.index[phones["source_id"] == int(source_id)].tolist()
    if not indices:
        return []

    index = indices[0]
    related = sorted(
        enumerate(similarities[index]),
        key=lambda item: item[1],
        reverse=True,
    )[1 : top_n + 1]

    items = []
    for position, similarity in related:
        row = phones.iloc[position]
        items.append(
            {
                "source_id": int(row["source_id"]),
                "name": row["name"],
                "brand": row["brand"],
                "price": float(row["price"]),
                "similarity": round(float(similarity), 4),
            }
        )
    return items
