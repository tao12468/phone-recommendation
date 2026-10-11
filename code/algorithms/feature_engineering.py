"""手机推荐系统的特征工程。"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


CHINESE_NUMBERS = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}

SCENE_MAP = {
    "游戏手机": "game",
    "拍照手机": "camera",
    "音乐手机": "music",
    "商务手机": "business",
    "自拍手机": "selfie",
    "快充手机": "fastcharge",
    "5G手机": "5g",
    "折叠屏手机": "fold",
    "大屏手机": "bigscreen",
    "老人机": "elderly",
    "三防手机": "rugged",
}


def price_level(price: float) -> str:
    if price < 2000:
        return "入门"
    if price < 4500:
        return "中端"
    if price < 8000:
        return "高端"
    return "旗舰"


def cpu_tier(cpu: str) -> float:
    text = str(cpu).upper()
    if re.search(r"(骁龙|SNAPDRAGON)\s*8|天玑\s*9|DIMENSITY\s*9|麒麟\s*9|KIRIN\s*9|A1[6-9]|A20", text):
        return 0.9
    if re.search(r"(骁龙|SNAPDRAGON)\s*7|天玑\s*[78]|DIMENSITY\s*[78]|麒麟\s*8|KIRIN\s*8|A1[3-5]", text):
        return 0.65
    if re.search(r"(骁龙|SNAPDRAGON)\s*[46]|天玑\s*6|DIMENSITY\s*6|麒麟\s*7|A1[0-2]|A[89]", text):
        return 0.45
    return 0.55


def os_type(value: str) -> str:
    text = str(value)
    if "iOS" in text or "iPhone" in text:
        return "iOS"
    if "HarmonyOS" in text or "鸿蒙" in text:
        return "鸿蒙"
    if any(
        item in text
        for item in ["Android", "安卓", "OriginOS", "MagicOS", "ColorOS", "HyperOS", "MIUI", "Funtouch"]
    ):
        return "安卓"
    return "其他"


def core_count(value) -> int | None:
    text = str(value)
    if "八核" in text:
        return 8
    if "十核" in text:
        return 10
    match = re.search(r"(\d+)\s*核", text)
    if match:
        return int(match.group(1))
    return None


def release_year(value) -> int | None:
    match = re.search(r"(20\d{2})", str(value))
    if match:
        return int(match.group(1))
    return None


def resolution_size(value) -> tuple[int | None, int | None]:
    match = re.search(r"(\d+)\s*[xX×]\s*(\d+)", str(value))
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def fill_median(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        if column in frame:
            frame[column] = frame[column].fillna(frame[column].median())
    return frame


def cluster_position(frame: pd.DataFrame) -> pd.Series:
    cluster_columns = ["price", "screen_size", "battery", "ram", "rom"]
    scaled = StandardScaler().fit_transform(frame[cluster_columns])
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled)

    cluster_price = (
        pd.DataFrame({"cluster": clusters, "price": frame["price"]})
        .groupby("cluster")["price"]
        .mean()
        .sort_values()
    )
    position_map = {
        cluster: label
        for cluster, label in zip(cluster_price.index, ["入门", "中端", "旗舰"])
    }
    return pd.Series(clusters).map(position_map)


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    """从清洗后的数据生成推荐特征。"""

    result = frame.copy()

    for column in ["price", "screen_size", "battery", "ram", "rom"]:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    result["price_level"] = result["price"].apply(price_level)
    result["brand_id"] = result["brand"].astype("category").cat.codes

    result["cpu_score"] = result["cpu"].apply(cpu_tier)
    result["performance_score"] = (
        result["cpu_score"] * 0.7 + (result["ram"].clip(upper=16) / 16) * 0.3
    )

    raw_value = result["performance_score"] / (result["price"] / 1000)
    result["value_for_money"] = (raw_value - raw_value.min()) / (
        raw_value.max() - raw_value.min()
    )

    result["position"] = cluster_position(result)
    result["os_type"] = result["os"].apply(os_type)
    result["core_count_num"] = result["core_count"].apply(core_count)

    resolution = result["resolution"].apply(resolution_size)
    result["resolution_width"] = resolution.apply(lambda item: item[0])
    result["resolution_height"] = resolution.apply(lambda item: item[1])
    result["release_year"] = result["release_date"].apply(release_year)

    for label, key in SCENE_MAP.items():
        result[f"scene_{key}"] = result["usage_scenes"].str.contains(
            label, na=False
        ).astype(int)

    result = fill_median(
        result,
        [
            "core_count_num",
            "resolution_width",
            "resolution_height",
            "release_year",
        ],
    )
    result["core_count_num"] = result["core_count_num"].round(0).astype(int)
    result["resolution_width"] = result["resolution_width"].round(0).astype(int)
    result["resolution_height"] = result["resolution_height"].round(0).astype(int)
    result["release_year"] = result["release_year"].round(0).astype(int)

    feature_columns = [
        "source_id",
        "name",
        "brand",
        "brand_id",
        "price",
        "screen_size",
        "battery",
        "ram",
        "rom",
        "price_level",
        "position",
        "performance_score",
        "value_for_money",
        "os_type",
        "core_count_num",
        "resolution_width",
        "resolution_height",
        "release_year",
        *[f"scene_{key}" for key in SCENE_MAP.values()],
    ]
    return result[feature_columns]
