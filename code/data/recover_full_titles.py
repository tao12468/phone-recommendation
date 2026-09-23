"""从 Git 历史中恢复列表页的完整标题，用于补充屏幕、电池等缺失值。"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def main() -> None:
    raw_path = Path("data/phones_raw.json")
    raw_items = json.loads(raw_path.read_text(encoding="utf-8"))

    full_text = subprocess.check_output(
        ["git", "show", "HEAD:code/data/zol_phone_list.json"],
        text=True,
        encoding="utf-8",
    )
    full_items = json.loads(full_text)
    title_map = {item["id"]: item.get("name", "") for item in full_items}

    updated = 0
    for item in raw_items:
        product_id = item.get("id")
        title = title_map.get(product_id)
        if title:
            item["title"] = title
            updated += 1

    raw_path.write_text(
        json.dumps(raw_items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"已恢复 {updated}/{len(raw_items)} 条完整标题")


if __name__ == "__main__":
    main()
