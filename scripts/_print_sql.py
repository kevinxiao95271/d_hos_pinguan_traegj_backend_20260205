# -*- coding: utf-8 -*-
import sys, re, pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
csv_df = pd.read_csv(ROOT / "专家数据含机构ID0410.csv", encoding="utf-8-sig")
csv_df.columns = [c.strip() for c in csv_df.columns]
prod = {}
for _, r in csv_df.iterrows():
    pn = re.sub(r"\D", "", str(r.get("phone", "")))
    if pn:
        prod[pn] = {k: (None if pd.isna(v) else v) for k, v in r.items()}

# 机构修正
INST_FIX = {
    "13958009748": (25, 24, "浙江大学医学院附属第二医院"),  # 李伟
}

print("-- ── 机构修正 ──────────────────────────────────────────────────")
for phone, (bad, good, iname) in INST_FIX.items():
    row = prod.get(phone, {})
    cur = int(row.get("institution_id") or 0)
    status = f"当前={cur}，{'需执行' if cur == bad else '已正确，无需执行'}"
    print(f"-- 李伟 {phone}  institution_id {bad} → {good}  ({iname})  [{status}]")
    print(f"UPDATE user_accounts SET institution_id = {good} WHERE phone = '{phone}' AND role = 'REVIEWER';")

print()
print("-- ── 验证 ──────────────────────────────────────────────────────")
print("SELECT id, name, phone, institution_id FROM user_accounts WHERE phone = '13958009748';")
