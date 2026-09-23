"""中关村在线手机数据爬虫。

使用流程：
1. 先抓取手机列表：python zol_spider.py list --out data/zol_phone_list.json
2. 再补全参数：python zol_spider.py details --list data/zol_phone_list.json --out data/phones_raw.json

说明：
- 当前只抓取公开的手机报价和参数，用于课程设计与学习。
- 请求之间有延迟，避免对目标网站造成压力。
- 如果网站结构变化，需要根据实际页面调整解析规则。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://detail.zol.com.cn"
LIST_PAGE_1 = f"{BASE_URL}/cell_phone_index/subcate57_list_1.html"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

BRAND_ALIASES = [
    "Redmi",
    "红米",
    "HUAWEI",
    "华为",
    "荣耀",
    "苹果",
    "iPhone",
    "OPPO",
    "vivo",
    "iQOO",
    "一加",
    "真我",
    "realme",
    "三星",
    "Samsung",
    "魅族",
    "努比亚",
    "红魔",
    "黑鲨",
    "ROG",
    "中兴",
    "联想",
    "摩托罗拉",
    "Moto",
    "诺基亚",
    "索尼",
    "HTC",
    "LG",
    "谷歌",
    "Google",
    "Nothing",
    "小米",
]


def fetch(url: str, retries: int = 3, delay: float = 0.4, encoding: str = "gbk") -> str:
    """下载网页，失败时自动重试。"""

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
            response.encoding = encoding
            return response.text
        except Exception as exc:
            if attempt == retries:
                raise RuntimeError(f"下载失败：{url}，原因：{exc}") from exc
            time.sleep(delay * attempt)
    raise RuntimeError(f"下载失败：{url}")


def list_url(page: int) -> str:
    """根据页码生成列表页地址。"""

    if page <= 1:
        return LIST_PAGE_1
    return f"{BASE_URL}/cell_phone_index/subcate57_0_list_1_0_1_2_0_{page}.html"


def brand_list_url(brand_id: str, page: int) -> str:
    """根据品牌 ID 和页码生成品牌列表页地址。"""

    if page <= 1:
        return f"{BASE_URL}/cell_phone_index/subcate57_{brand_id}_list_1.html"
    return (
        f"{BASE_URL}/cell_phone_index/"
        f"subcate57_{brand_id}_list_1_0_1_2_0_{page}.html"
    )


def guess_brand(name: str) -> str:
    """从手机名称中推测品牌。"""

    if not name:
        return ""
    lower_name = name.lower()
    aliases = {
        "redmi": "红米",
        "红米": "红米",
        "huawei": "华为",
        "华为": "华为",
        "荣耀": "荣耀",
        "iphone": "苹果",
        "苹果": "苹果",
        "oppo": "OPPO",
        "vivo": "vivo",
        "iqoo": "iQOO",
        "一加": "一加",
        "真我": "真我",
        "realme": "真我",
        "samsung": "三星",
        "三星": "三星",
        "魅族": "魅族",
        "努比亚": "努比亚",
        "红魔": "红魔",
        "黑鲨": "黑鲨",
        "rog": "ROG",
        "中兴": "中兴",
        "联想": "联想",
        "摩托罗拉": "摩托罗拉",
        "moto": "摩托罗拉",
        "诺基亚": "诺基亚",
        "索尼": "索尼",
        "htc": "HTC",
        "google": "谷歌",
        "谷歌": "谷歌",
        "nothing": "Nothing",
        "小米": "小米",
    }
    for key, brand in aliases.items():
        if key in lower_name:
            return brand
    return ""


def parse_price(text: str) -> float | None:
    """从“参考价：￥6999”中提取价格。"""

    match = re.search(r"参考价[：:]\s*[￥¥]?\s*([0-9]+(?:\.[0-9]+)?)(万?)", text)
    if not match:
        return None
    price = float(match.group(1))
    if match.group(2):
        price *= 10000
    return round(price, 2)


def parse_list_page(html: str) -> list[dict]:
    """解析手机列表页，提取名称、价格和详情页地址。"""

    soup = BeautifulSoup(html, "html.parser")
    items: list[dict] = []

    for li in soup.find_all("li"):
        text = li.get_text(" ", strip=True)
        if "参考价" not in text:
            continue

        link = li.select_one('h3 a[href*="/cell_phone/index"]')
        if not link:
            continue

        url = urljoin(BASE_URL, link["href"])
        name = next(
            (child.strip() for child in link.contents if isinstance(child, str)),
            link.get_text(" ", strip=True),
        )
        price = parse_price(text)
        product_id_match = re.search(r"index(\d+)\.shtml", url)
        product_id = int(product_id_match.group(1)) if product_id_match else 0

        items.append(
            {
                "id": product_id,
                "name": name,
                "brand": guess_brand(name),
                "price": price,
                "url": url,
            }
        )

    # 同一页面可能出现多个相同详情链接，按 URL 去重。
    seen: set[str] = set()
    unique_items: list[dict] = []
    for item in items:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique_items.append(item)
    return unique_items


def param_url(product_id: int) -> str:
    """根据产品 ID 生成参数页地址。"""

    group = math.ceil(product_id / 1000)
    return f"{BASE_URL}/{group}/{product_id}/param.shtml"


def parse_detail_page(html: str, product: dict) -> dict:
    """解析参数页，补全手机参数。"""

    soup = BeautifulSoup(html, "html.parser")
    result = dict(product)
    result["source"] = "ZOL"

    params: dict[str, str] = {}
    for row in soup.select("tr"):
        label_node = row.find("th")
        value_node = row.find("td")
        if not label_node or not value_node:
            continue
        label = label_node.get_text(strip=True)
        value = value_node.get_text(" ", strip=True).replace("纠错", "").strip()
        params[label] = value

    result["screen_size"] = parse_number(params.get("屏幕尺寸") or params.get("主屏尺寸"))
    result["resolution"] = params.get("分辨率") or params.get("主屏分辨率") or ""
    result["battery"] = parse_number(params.get("电池容量"))
    result["core_count"] = params.get("CPU核心数") or params.get("核心数", "")
    result["camera"] = (
        params.get("摄像头名称")
        or params.get("像素")
        or params.get("后置摄像头")
        or params.get("前置摄像头")
        or ""
    )
    result["cpu"] = params.get("CPU型号") or params.get("CPU", "")
    result["ram"] = parse_number(params.get("RAM容量") or params.get("内存"))
    result["rom"] = parse_number(params.get("ROM容量"))
    result["os"] = params.get("操作系统", "")
    result["usage_scenes"] = params.get("使用场景", "")
    result["release_date"] = params.get("国内发布时间") or params.get("上市日期") or ""

    return result


def parse_number(value: str | None) -> float | None:
    """从“6.78英寸”“8000mAh”“12GB”中提取数字。"""

    if not value:
        return None
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", value)
    if not match:
        return None
    number = float(match.group(1))
    if "TB" in value.upper():
        number *= 1024
    return round(number, 2)


def parse_labeled_value(text: str, label: str) -> str:
    """从“CPU：骁龙 8 Gen 3 RAM容量：12GB”中取某个标签的值。"""

    for part in text.split("|"):
        part = part.strip()
        if part.startswith(f"{label}：") or part.startswith(f"{label}:"):
            return part.split("：", 1)[-1].split(":", 1)[-1].strip()
    return ""


def crawl_list(
    max_pages: int,
    delay: float = 0.3,
    brand_ids: list[str] | None = None,
) -> list[dict]:
    """抓取手机列表。

    不传 brand_ids 时抓取全部手机；传入品牌 ID 时抓取指定品牌。
    """

    items: list[dict] = []
    sources = [("全部", None)] if not brand_ids else [("品牌", bid) for bid in brand_ids]

    for label, brand_id in sources:
        for page in range(1, max_pages + 1):
            if brand_id is None:
                url = list_url(page)
            else:
                url = brand_list_url(brand_id, page)
            print(f"[列表] {label} 第 {page} 页：{url}")
            html = fetch(url)
            page_items = parse_list_page(html)
            print(f"[列表] 本页获取 {len(page_items)} 条")
            items.extend(page_items)
            if page < max_pages:
                time.sleep(delay)

    unique: dict[str, dict] = {}
    for item in items:
        unique[item["url"]] = item
    return list(unique.values())


def enrich_one(product: dict, delay: float) -> dict:
    """抓取一个参数页。"""

    url = param_url(product["id"])
    html = fetch(url)
    time.sleep(delay)
    return parse_detail_page(html, product)


def enrich_details(
    products: list[dict],
    max_items: int,
    workers: int = 3,
    delay: float = 0.25,
) -> list[dict]:
    """并发抓取详情页。"""

    products = products[:max_items]
    results: list[dict] = []
    errors: list[str] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(enrich_one, product, delay): product
            for product in products
        }
        for index, future in enumerate(as_completed(future_map), start=1):
            product = future_map[future]
            try:
                results.append(future.result())
                if index == 1 or index == len(products) or index % 20 == 0:
                    print(f"[详情] {index}/{len(products)} 完成")
            except Exception as exc:
                errors.append(f"{product.get('name')}: {exc}")
                print(f"[详情] {index}/{len(products)} 失败：{product.get('name')}，原因：{exc}")

    if errors:
        print(f"[详情] 共失败 {len(errors)} 条")
    return results


def save_json(items: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"已保存 {len(items)} 条数据到：{output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="中关村在线手机数据爬虫")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="抓取手机列表")
    list_parser.add_argument("--max-pages", type=int, default=25)
    list_parser.add_argument("--brands", type=str, default=None)
    list_parser.add_argument("--out", type=Path, default=Path("data/zol_phone_list.json"))

    detail_parser = subparsers.add_parser("details", help="补全手机参数")
    detail_parser.add_argument("--list", dest="list_file", type=Path, required=True)
    detail_parser.add_argument("--max-items", type=int, default=1000)
    detail_parser.add_argument("--workers", type=int, default=3)
    detail_parser.add_argument("--out", type=Path, default=Path("data/phones_raw.json"))

    args = parser.parse_args()

    if args.command == "list":
        brand_ids = None
        if args.brands:
            brand_ids = [item.strip() for item in args.brands.split(",") if item.strip()]
        items = crawl_list(max_pages=args.max_pages, brand_ids=brand_ids)
        save_json(items, args.out)
        return

    if args.command == "details":
        products = json.loads(args.list_file.read_text(encoding="utf-8"))
        items = enrich_details(
            products,
            max_items=args.max_items,
            workers=args.workers,
        )
        save_json(items, args.out)


if __name__ == "__main__":
    main()
