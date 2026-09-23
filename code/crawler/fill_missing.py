"""补充因网络原因漏抓的手机详情。

使用示例：
python crawler/fill_missing.py --list data/zol_phone_list.json --raw data/phones_raw.json --count 1
"""

import argparse
import json
import time
from pathlib import Path

from crawler import zol_spider


def main() -> None:
    parser = argparse.ArgumentParser(description="补充漏抓的手机详情")
    parser.add_argument("--list", dest="list_file", type=Path, required=True)
    parser.add_argument("--raw", dest="raw_file", type=Path, required=True)
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    products = json.loads(args.list_file.read_text(encoding="utf-8"))
    raw_items = json.loads(args.raw_file.read_text(encoding="utf-8"))
    existing_ids = {item["id"] for item in raw_items}
    missing = [item for item in products if item["id"] not in existing_ids]

    added = 0
    for product in missing[: args.count]:
        try:
            html = zol_spider.fetch(zol_spider.param_url(product["id"]))
            record = zol_spider.parse_detail_page(html, product)
            raw_items.append(record)
            added += 1
            print(f"已补充：{record.get('name')}")
        except Exception as exc:
            print(f"补充失败：{product.get('name')}，原因：{exc}")
        time.sleep(0.3)

    args.raw_file.write_text(
        json.dumps(raw_items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"本次补充 {added} 条，当前共 {len(raw_items)} 条")


if __name__ == "__main__":
    main()
