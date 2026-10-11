"""基于用户的协同过滤推荐。"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from algorithms.content_recommender import load_phones


def build_user_item_matrix(interactions: pd.DataFrame) -> pd.DataFrame:
    """把交互记录转成用户-手机权重矩阵。"""

    if interactions.empty:
        return pd.DataFrame()

    matrix = interactions.pivot_table(
        index="user_id",
        columns="phone_source_id",
        values="weight",
        aggfunc="max",
        fill_value=0,
    )
    return matrix


def recommend_for_user(
    user_id: int,
    top_n: int = 5,
    interactions: pd.DataFrame | None = None,
    phones: pd.DataFrame | None = None,
) -> list[dict]:
    """为指定用户推荐手机。"""

    if interactions is None:
        return []
    phones = phones if phones is not None else load_phones()
    matrix = build_user_item_matrix(interactions)

    if matrix.empty or user_id not in matrix.index:
        return []

    user_similarity = cosine_similarity(matrix.values)
    similarity_frame = pd.DataFrame(
        user_similarity,
        index=matrix.index,
        columns=matrix.index,
    )

    target_row = matrix.loc[user_id]
    interacted_phones = set(target_row[target_row > 0].index)
    candidate_columns = [column for column in matrix.columns if column not in interacted_phones]

    if not candidate_columns:
        return []

    predicted: dict[int, float] = {}
    for phone_id in candidate_columns:
        numerator = 0.0
        denominator = 0.0
        for other_user in matrix.index:
            if other_user == user_id:
                continue
            similarity = similarity_frame.loc[user_id, other_user]
            if similarity <= 0:
                continue
            rating = matrix.loc[other_user, phone_id]
            numerator += similarity * rating
            denominator += abs(similarity)

        if denominator > 0:
            predicted[int(phone_id)] = float(numerator / denominator)

    ranked = sorted(predicted.items(), key=lambda item: item[1], reverse=True)[:top_n]
    if not ranked:
        return []

    phone_lookup = {
        int(row["source_id"]): row for _, row in phones.iterrows()
    }
    items = []
    for phone_id, score in ranked:
        row = phone_lookup.get(phone_id)
        if row is None:
            continue
        items.append(
            {
                "source_id": phone_id,
                "name": row["name"],
                "brand": row["brand"],
                "price": float(row["price"]),
                "predicted_score": round(score, 4),
                "reason": "相似用户也喜欢",
            }
        )
    return items
