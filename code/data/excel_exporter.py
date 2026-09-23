"""把清洗后的手机数据导出为 Excel。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_excel(frame: pd.DataFrame, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_excel(output, index=False)
    return output
