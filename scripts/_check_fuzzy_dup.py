# -*- coding: utf-8 -*-
"""
同机构内项目名相似度检测（去空格/标点/全半角归一化后比对）
"""
import sys, re, pandas as pd
from pathlib import Path
from itertools import combinations
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
f = next(ROOT.glob("项目数据（含机构ID+手法+主题0410*.csv"))
df = pd.read_csv(f, encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]

def normalize(s: str) -> str:
    """去空格、统一全半角数字/字母、去常见标点"""
    s = str(s).strip()
    s = s.replace(" ", "").replace("\u3000", "")
    # 全角→半角
    s = s.translate(str.maketrans(
        "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    ))
    # 罗马数字统一（Ⅰ→I，Ⅱ→II 等）
    s = s.replace("Ⅰ","I").replace("Ⅱ","II").replace("Ⅲ","III").replace("Ⅳ","IV")
    s = s.replace("一类","I类").replace("二类","II类").replace("三类","III类")
    # 去标点
    s = re.sub(r"[，。、；：""''《》【】（）().,;:!?！？\-—–]", "", s)
    return s.lower()

def similarity(a: str, b: str) -> float:
    """简单字符集 Jaccard（以字为单位）"""
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

def longest_common_subseq_ratio(a: str, b: str) -> float:
    """LCS 占较短串的比例"""
    m, n = len(a), len(b)
    if m == 0 or n == 0:
        return 0.0
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n] / min(m, n)

THRESHOLD = 0.82   # LCS 占比阈值

df["_norm"] = df["project_name"].apply(normalize)

suspects = []
for inst, grp in df.groupby("institution_id"):
    rows = grp.reset_index(drop=True)
    if len(rows) < 2:
        continue
    for i, j in combinations(range(len(rows)), 2):
        a, b = rows.at[i, "_norm"], rows.at[j, "_norm"]
        score = longest_common_subseq_ratio(a, b)
        if score >= THRESHOLD:
            suspects.append({
                "机构": rows.at[i, "institution_name"],
                "编号A": rows.at[i, "registration_id"],
                "项目名A": rows.at[i, "project_name"],
                "编号B": rows.at[j, "registration_id"],
                "项目名B": rows.at[j, "project_name"],
                "相似度": round(score, 3),
            })

if suspects:
    res = pd.DataFrame(suspects).sort_values("相似度", ascending=False)
    print(f"发现疑似重复: {len(res)} 组\n")
    for _, r in res.iterrows():
        print(f"[{r['机构']}]  相似度={r['相似度']}")
        print(f"  {r['编号A']}: {r['项目名A']}")
        print(f"  {r['编号B']}: {r['项目名B']}")
        print()
else:
    print("未发现疑似重复项目。")
