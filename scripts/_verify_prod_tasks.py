# -*- coding: utf-8 -*-
"""
核实生产库已分配任务与 grouping_final 是否一致
"""
import sys, re, pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]

# ── 1. 读生产库导出 ──────────────────────────────────────────────────────────
stat_df = pd.read_csv(ROOT / "生产环境任务已分配统计0414.csv", encoding="utf-8-sig")
stat_df.columns = [c.strip() for c in stat_df.columns]
print("统计文件列名:", stat_df.columns.tolist())

list_df = pd.read_csv(ROOT / "生产环境项目已分配清单0414.csv", encoding="utf-8-sig")
list_df.columns = [c.strip() for c in list_df.columns]
print("清单文件列名:", list_df.columns.tolist())
print()

# ── 2. 读 grouping_final 预期数据 ────────────────────────────────────────────
gf = pd.read_excel(ROOT / "grouping_final.xlsx", sheet_name="分组明细")
gf.columns = [c.strip() for c in gf.columns]
expected = gf.groupby("建议分组")["项目编号"].apply(set).to_dict()
expected_cnt = {k: len(v) for k, v in expected.items()}

# ── 3. 读 4.13 专家名单 ──────────────────────────────────────────────────────
p_413 = next(ROOT.glob("*书审*名单*4.13*.xlsx"))
df_sh = pd.read_excel(p_413, sheet_name=0, header=None)
experts = {}   # gc → [name]
cur_gc = None
for i in range(len(df_sh)):
    r = df_sh.iloc[i]; g = r[0]
    if pd.notna(g) and str(g).strip() not in ("","nan"): cur_gc = str(g).strip()
    if not cur_gc: continue
    nm = r[3] if len(r)>3 else None
    if pd.isna(nm) or str(nm).strip() in ("","专家","姓名","nan"): continue
    pn = re.sub(r"\D","",str(r[7])) if len(r)>7 and pd.notna(r[7]) else ""
    if not pn: continue
    experts.setdefault(cur_gc, []).append(str(nm).strip())
expected_reviewer_cnt = {gc: len(v) for gc, v in experts.items()}

# ── 4. 分析统计文件 ──────────────────────────────────────────────────────────
print("=" * 65)
print("── 分组统计核实（生产 vs grouping_final）──────────────────────")
print(f"{'分组':<6} {'预期项目':>6} {'实际项目':>6} {'预期专家':>6} {'实际专家':>6} {'任务数':>7}  状态")
print("-" * 65)

# 找列名
gc_col  = next((c for c in stat_df.columns if "group" in c.lower() or "分组" in c), None)
pc_col  = next((c for c in stat_df.columns if "project" in c.lower() or "项目" in c), None)
rc_col  = next((c for c in stat_df.columns if "reviewer" in c.lower() or "专家" in c), None)
tc_col  = next((c for c in stat_df.columns if "task" in c.lower() or "任务" in c), None)

issues = []
all_ok = True
for _, row in stat_df.sort_values(gc_col).iterrows():
    gc   = str(row[gc_col]).strip()
    p_act = int(row[pc_col]) if pc_col else 0
    r_act = int(row[rc_col]) if rc_col else 0
    t_act = int(row[tc_col]) if tc_col else 0
    p_exp = expected_cnt.get(gc, 0)
    r_exp = expected_reviewer_cnt.get(gc, 0)
    ok = (p_act == p_exp) and (r_act == r_exp) and (t_act == p_exp * r_exp)
    flag = "✅" if ok else "⚠️"
    if not ok:
        all_ok = False
        issues.append(f"  {gc}: 项目{p_exp}→{p_act}, 专家{r_exp}→{r_act}, 任务应={p_exp*r_exp} 实={t_act}")
    print(f"{gc:<6} {p_exp:>6} {p_act:>6} {r_exp:>6} {r_act:>6} {t_act:>7}  {flag}")

print("=" * 65)
if all_ok:
    print("\n✅ 全部一致，无问题")
else:
    print(f"\n⚠️ 发现 {len(issues)} 个差异：")
    for s in issues:
        print(s)

# ── 5. 检查清单：有无项目未分配或多分配 ────────────────────────────────────
print()
print("── 项目覆盖核实 ──────────────────────────────────────────────")
# 找清单中的 registration_id 列
rid_col = next((c for c in list_df.columns if "registration" in c.lower() or "项目" in c.lower()), None)
if rid_col:
    prod_ids = set(list_df[rid_col].astype(int).tolist())
    exp_ids  = set(gf["项目编号"].astype(int).tolist())
    missing  = exp_ids - prod_ids
    extra    = prod_ids - exp_ids
    print(f"grouping_final 项目数: {len(exp_ids)}")
    print(f"生产已分配项目数: {len(prod_ids)}")
    if missing:
        print(f"⚠️  未分配到任务的项目 ({len(missing)} 个): {sorted(missing)}")
    else:
        print("✅ grouping_final 所有项目均已分配")
    if extra:
        print(f"⚠️  生产有但 grouping_final 没有的项目 ({len(extra)} 个): {sorted(extra)}")
