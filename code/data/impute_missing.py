"""缺失值填充模块。

填充顺序：
1. 优先使用同品牌的字段中位数；
2. 如果该品牌没有可用数据，再使用全量中位数。

这里的填充属于数据预处理中的统计填补，不虚构具体型号的真实参数。
"""

from __future__ import annotations

import pandas as pd


NUMERIC_COLUMNS = ["screen_size", "battery", "ram", "rom"]


def fill_missing_values(frame: pd.DataFrame) -> pd.DataFrame:
    """填充数值字段的缺失值。"""

    result = frame.copy()

    for column in NUMERIC_COLUMNS:
        if column not in result:
            result[column] = pd.NA

        brand_median = result.groupby("brand")[column].median()
        overall_median = result[column].median()

        result[column] = (
            result[column]
            .fillna(result["brand"].map(brand_median))
            .fillna(overall_median)
        )

    result["screen_size"] = result["screen_size"].round(1)
    result["battery"] = result["battery"].round(0)
    result["ram"] = result["ram"].round(1)
    result["rom"] = result["rom"].round(0)

    return result


def missing_report(frame: pd.DataFrame) -> dict[str, int]:
    """统计数值字段的缺失数量。"""

    return {
        column: int(frame[column].isna().sum())
        for column in NUMERIC_COLUMNS
        if column in frame
    }
