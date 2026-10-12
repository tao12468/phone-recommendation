"""生成示例交互数据，用于演示协同过滤。"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from data.interaction_repository import insert_interactions


def main() -> None:
    parser = argparse.ArgumentParser(description="生成示例交互数据")
    parser.add_argument("--features", type=Path, default=Path("data/phones_features.json"))
    parser.add_argument("--users", type=int, default=30)
    parser.add_argument("--interactions", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default="phone_recommender")
    args = parser.parse_args()

    features = json.loads(args.features.read_text(encoding="utf-8"))
    phone_ids = [item["source_id"] for item in features]
    rng = random.Random(args.seed)

    events = ["view", "click", "compare", "favorite"]
    records = []
    for _ in range(args.interactions):
        records.append(
            {
                "user_id": 100000 + rng.randint(1, args.users),
                "phone_source_id": rng.choice(phone_ids),
                "event_type": rng.choice(events),
            }
        )

    count = insert_interactions(
        records,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
    )
    print(f"已写入 {count} 条示例交互数据")


if __name__ == "__main__":
    main()
