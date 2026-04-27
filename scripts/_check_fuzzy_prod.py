# -*- coding: utf-8 -*-
import sys, re, pandas as pd
from pathlib import Path
from itertools import combinations
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "项目提交人信息0413.csv", encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]
print(f"总行数: {len(df)}\n")

def normalize(s: str) -> str:
    s = str(s).strip().replace(" ", "").replace("\u3000", "")
    s = s.translate(str.maketrans(
        "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    ))
    s = s.replace("Ⅰ","I").replace("Ⅱ","II").replace("Ⅲ","III").replace("Ⅳ","IV")
    s = s.replace("一类","I类").replace("二类","II类").replace("三类","III类")
    s = re.sub(r'[，。、；：""''《》【】（）().,;:!?！？\-—–]', "", s)
    return s.lower()

def lcs_ratio(a, b):
    m, n = len(a), len(b)
    if not m or not n: return 0.0
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = dp[i-1][j-1]+1 if a[i-1]==b[j-1] else max(dp[i-1][j], dp[i][j-1])
    return dp[m][n] / min(m, n)

THRESHOLD = 0.82
df["_norm"] = df["project_name"].apply(normalize)

suspects = []
for inst, grp in df.groupby("institution_name"):
    rows = grp.reset_index(drop=True)
    if len(rows) < 2: continue
    for i, j in combinations(range(len(rows)), 2):
        score = lcs_ratio(rows.at[i,"_norm"], rows.at[j,"_norm"])
        if score >= THRESHOLD:
            suspects.append({
                "机构": inst,
                "编号A": rows.at[i,"registration_id"],
                "项目名A": rows.at[i,"project_name"],
                "提交人A": f"{rows.at[i,'submitter_name']}({rows.at[i,'submitter_phone']})",
                "编号B": rows.at[j,"registration_id"],
                "项目名B": rows.at[j,"project_name"],
                "提交人B": f"{rows.at[j,'submitter_name']}({rows.at[j,'submitter_phone']})",
                "相似度": round(score, 3),
            })

if suspects:
    res = pd.DataFrame(suspects).sort_values("相似度", ascending=False)
    print(f"疑似重复: {len(res)} 组\n")
    for _, r in res.iterrows():
        print(f"【{r['机构']}】相似度={r['相似度']}")
        print(f"  A {r['编号A']}: {r['项目名A']}")
        print(f"       提交人: {r['提交人A']}")
        print(f"  B {r['编号B']}: {r['项目名B']}")
        print(f"       提交人: {r['提交人B']}")
        print()
else:
    print("未发现疑似重复。")
