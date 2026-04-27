# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
gap = pd.read_excel(ROOT / "grouping_final.xlsx", sheet_name="差距说明")
out = open(Path(__file__).with_name("_gap_content.txt"), "w", encoding="utf-8")
out.write(f"差距说明共 {len(gap)} 行\n\n")
out.write(gap.to_string(index=False) + "\n")
out.close()
print("done")
