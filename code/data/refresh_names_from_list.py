"""用列表页的干净名称刷新 phones_raw.json 中的名称。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="刷新原始数据中的手机名称")
    parser.add_argument("--list", type=Path, default=Path("data/zol_phone_list.json"))
    parser.add_argument("--raw", type=Path, default=Path("data/phones_raw.json"))
    args = parser.parse_args()

    list_items = json.loads(args.list.read_text(encoding="utf-8"))
    raw_items = json.loads(args.raw.read_text(encoding="utf-8"))

    name_map = {item["id"]: item["name"] for item in list_items}
    brand_map = {item["id"]: item["brand"] for item in list_items}

    updated = 0
    for item in raw_items:
        product_id = item.get("id")
        if product_id in name_map and name_map[product_id]:
            item["name"] = name_map[product_id]
            if not item.get("brand") and brand_map.get(product_id):
                item["brand"] = brand_map[product_id]
            updated += 1

    args.raw.write_text(
        json.dumps(raw_items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"已刷新 {updated}/{len(raw_items)} 条名称")


if __name__ == "__main__":
    main()
