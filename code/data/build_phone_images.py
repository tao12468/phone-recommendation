"""从列表数据生成手机图片地址映射。"""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    list_path = Path("data/zol_phone_list.json")
    output_path = Path("data/phone_images.json")
    items = json.loads(list_path.read_text(encoding="utf-8"))

    image_map = {
        str(item["id"]): item.get("image_url", "")
        for item in items
        if item.get("image_url")
    }
    output_path.write_text(
        json.dumps(image_map, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"已生成 {len(image_map)} 条图片地址")


if __name__ == "__main__":
    main()
