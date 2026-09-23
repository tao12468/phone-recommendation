"""手机数据清洗规则。"""

from __future__ import annotations

import re

import pandas as pd
from crawler.zol_spider import guess_brand


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def clean_cpu(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    text = re.sub(r"更多.*$", "", text)
    text = re.sub(r"手机性能排行.*$", "", text)
    return text.strip(" ，,>")


def clean_core_count(value) -> str:
    return clean_text(value).strip(" >")


def clean_usage_scenes(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    text = text.replace(">", " ").replace("，", " ").replace(",", " ")
    tokens = [item for item in text.split() if item not in {"", "，", ","}]
    return ",".join(tokens)


def extract_product_name(value) -> str:
    """只保留手机型号名称，去掉颜色、内存、宣传语等描述。"""

    if pd.isna(value):
        return ""
    text = str(value).strip()

    match = re.search(
        r"^(.*?\(\d+\s*(?:GB|TB|G)[^)]*\)|.*?（[^）]*(?:GB|G|国际版|全网通)[^）]*）)",
        text,
    )
    if match:
        return match.group(1).strip()

    description_markers = [
        "iPhone的",
        "外观设计",
        "手机制式",
        "蔡司",
        "骁龙",
        "天玑",
        "麒麟",
        "徕卡",
        "HarmonyOS",
        "沉浸",
        "圆弧",
        "超薄",
        "大电池",
        "金标",
        "蓝晶",
        "超视网膜",
    ]
    match = re.search(rf"\s*({'|'.join(description_markers)})", text)
    if match:
        return text[: match.start()].strip()

    if len(text) <= 60:
        return text.strip()

    return text[:120].strip()


def valid_number(value, low: float, high: float) -> float | None:
    if pd.isna(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number < low or number > high:
        return None
    return round(number, 2)


def parse_ram_rom_from_name(value) -> tuple[float | None, float | None]:
    """从手机名称中解析内存和存储，例如 (12GB/256GB)、（16GB）。"""

    if pd.isna(value):
        return None, None
    text = str(value)

    match = re.search(
        r"[\(（]\s*(\d+(?:\.\d+)?)\s*GB\s*/\s*(\d+(?:\.\d+)?)\s*(GB|TB)\s*[\)）]",
        text,
        flags=re.I,
    )
    if match:
        ram = float(match.group(1))
        rom = float(match.group(2))
        if match.group(3).upper() == "TB":
            rom *= 1024
        return round(ram, 1), round(rom, 1)

    match = re.search(
        r"[\(（]\s*(\d+(?:\.\d+)?)\s*(GB|TB)\s*[\)）]",
        text,
        flags=re.I,
    )
    if match:
        rom = float(match.group(1))
        if match.group(2).upper() == "TB":
            rom *= 1024
        return None, round(rom, 1)

    return None, None


def parse_battery_from_title(value) -> float | None:
    if pd.isna(value):
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*mAh", str(value), flags=re.I)
    if not match:
        return None
    number = float(match.group(1))
    return number if 500 <= number <= 50000 else None


def parse_screen_from_title(value) -> float | None:
    if pd.isna(value):
        return None
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:英寸|inch)",
        str(value),
        flags=re.I,
    )
    if not match:
        return None
    number = float(match.group(1))
    return number if 1 <= number <= 15 else None


def clean_records(records: list[dict]) -> pd.DataFrame:
    """把原始记录清洗成适合入库的 DataFrame。"""

    frame = pd.DataFrame(records)
    frame = frame.rename(columns={"id": "source_id"})

    if "brand" not in frame:
        frame["brand"] = ""
    frame["brand"] = frame["brand"].fillna("")
    frame["brand"] = frame.apply(
        lambda row: row["brand"] or guess_brand(row.get("name", "")),
        axis=1,
    )

    frame["name"] = frame["name"].apply(extract_product_name).str.slice(0, 200)
    frame = frame[frame["name"].str.len() > 0]
    frame["price"] = frame["price"].apply(lambda value: valid_number(value, 1, 200000))
    frame["screen_size"] = frame["screen_size"].apply(
        lambda value: valid_number(value, 1, 15)
    )
    frame["battery"] = frame["battery"].apply(
        lambda value: valid_number(value, 500, 50000)
    )
    frame["ram"] = frame["ram"].apply(lambda value: valid_number(value, 1, 64))
    frame["rom"] = frame["rom"].apply(lambda value: valid_number(value, 1, 4096))

    parsed_memory = frame["name"].apply(parse_ram_rom_from_name)
    frame["ram_from_name"] = parsed_memory.apply(lambda item: item[0])
    frame["rom_from_name"] = parsed_memory.apply(lambda item: item[1])
    frame["ram"] = frame["ram"].fillna(frame["ram_from_name"])
    frame["rom"] = frame["rom"].fillna(frame["rom_from_name"])
    frame = frame.drop(columns=["ram_from_name", "rom_from_name"])

    if "title" not in frame:
        frame["title"] = ""
    frame["title"] = frame["title"].apply(clean_text)
    frame["battery"] = frame["battery"].fillna(
        frame["title"].apply(parse_battery_from_title)
    )
    frame["screen_size"] = frame["screen_size"].fillna(
        frame["title"].apply(parse_screen_from_title)
    )

    for column in [
        "resolution",
        "camera",
        "os",
        "release_date",
        "source",
        "url",
        "title",
    ]:
        if column not in frame:
            frame[column] = ""
        frame[column] = frame[column].apply(clean_text)

    frame["url"] = frame["url"].str.slice(0, 255)

    if "core_count" not in frame:
        frame["core_count"] = ""
    frame["core_count"] = frame["core_count"].apply(clean_core_count)

    if "cpu" not in frame:
        frame["cpu"] = ""
    frame["cpu"] = frame["cpu"].apply(lambda value: clean_cpu(value)[:200])

    if "usage_scenes" not in frame:
        frame["usage_scenes"] = ""
    frame["usage_scenes"] = frame["usage_scenes"].apply(clean_usage_scenes)

    frame["camera"] = frame["camera"].replace({"暂无数据": ""})
    frame["source"] = frame["source"].replace({"": "ZOL"})
    frame["brand"] = frame["brand"].replace({"": "未知"})
    frame = frame[frame["price"].notna()]
    frame = frame.drop_duplicates(subset=["source_id", "url"], keep="first")
    frame = frame.sort_values("source_id")

    columns = [
        "source_id",
        "name",
        "brand",
        "price",
        "screen_size",
        "resolution",
        "battery",
        "core_count",
        "camera",
        "cpu",
        "ram",
        "rom",
        "os",
        "usage_scenes",
        "release_date",
        "source",
        "url",
    ]
    return frame[columns]
