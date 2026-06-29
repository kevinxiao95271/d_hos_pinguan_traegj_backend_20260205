"""
生成决赛评委任务分配 SQL
读取 Excel 评委分派 -> 查生产库匹配 reviewer_id + registration_id -> 输出 INSERT SQL
"""
import openpyxl, pymysql, io, sys, os, re
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── DB 连接（生产库）──────────────────────────────────────────
conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606, user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

# ── 读取 Excel ────────────────────────────────────────────────
base = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205'
fname = next(f for f in os.listdir(base) if '评委分派' in f and f.endswith('.xlsx'))
wb = openpyxl.load_workbook(os.path.join(base, fname), data_only=True)
ws = wb['Sheet2']
rows = list(ws.iter_rows(values_only=True))

# Excel 专场名 → DB final_session_code 映射
SESSION_MAP = {
    '进阶组1':            '2026进阶组1组',
    '进阶组2':            '2026进阶组2组',
    '进阶组3':            '2026进阶组3组',
    '基层组1':            '2026基层组1组',
    '基层组2':            '2026基层组2组',
    '基层组3':            '2026基层组3组',
    '基层组4':            '2026基层组4组',
    'PDCA专场1':          '2026综合组PDCA专场1',
    'PDCA专场2':          '2026综合组PDCA专场2',
    'PDCA专场3':          '2026综合组PDCA专场3',
    '十大安全专场1':       '2026综合组十大安全目标专场1',
    '十大安全专场2':       '2026综合组十大安全目标专场2',
    '综合工具专场1':       '2026综合组综合工具专场1',
    '综合工具专场2':       '2026综合组综合工具专场2',
    '问题解决型专场1':     '2026综合组问题解决型专场1',
    '问题解决型专场2':     '2026综合组问题解决型专场2',
    '问题解决型专场3':     '2026综合组问题解决型专场3',
    '问题解决型专场4':     '2026综合组问题解决型专场4',
    'QFD、课题达成型专场1':'2026综合组QFD、课题达成型专场1',
    'QFD、课题达成型专场2':'2026综合组QFD、课题达成型专场2',
    'QFD、课题达成型专场3':'2026综合组QFD、课题达成型专场3',
}

# 解析 Excel: session_code -> [expert_name_raw, ...]
# 结构：行4=场地, 行5=专场, 行6~10=专家1~5，列B~H
session_experts = defaultdict(list)   # db_session_code -> [raw_name]

# 根据实际行内容定位每块的专场行和专家行（0-based 行索引）
# Block1: 专场行=rows[4], 专家行=rows[5..9]
# Block2: 专场行=rows[15], 专家行=rows[16..20]
# Block3: 专场行=rows[26], 专家行=rows[27..31]
BLOCK_DEFS = [
    {'session_row': 4,  'expert_rows': range(5, 10)},
    {'session_row': 15, 'expert_rows': range(16, 21)},
    {'session_row': 26, 'expert_rows': range(27, 32)},
]

for blk in BLOCK_DEFS:
    session_name_row = rows[blk['session_row']]
    expert_row_list = [rows[i] for i in blk['expert_rows'] if i < len(rows)]

    # 列C(index2)~I(index8) 对应7个会场（index1是标签列"专场"）
    for col in range(2, 9):
        sess_raw = session_name_row[col]
        if not sess_raw:
            continue
        sess_raw = str(sess_raw).strip()
        db_code = SESSION_MAP.get(sess_raw)
        if not db_code:
            print(f"[警告] 未映射的专场: {sess_raw!r}")
            continue
        for er in expert_row_list:
            name_raw = er[col]
            if name_raw:
                session_experts[db_code].append(str(name_raw).strip())

print("=== 分派解析结果 ===")
for sc, names in sorted(session_experts.items()):
    print(f"  {sc}: {names}")

# ── 评委 ID 映射（来自生产库用户提供的全量数据，不限角色）────
# 格式：id, phone, name, title, institution
PROD_REVIEWER_RAW = """705	13757171988	丁志明
753	13958365721	严志瑜
739	13588216288	严涓
717	13067987798	俞雪芬
766	18768206616	傅爱蓉
692	13757119537	兰美娟
777	13819594925	冯少为
741	13867452301	冯志仙
755	13958202082	冯济业
812	13705713539	冯玉权
704	13957168708	冯素文
799	15105868265	刘仁杰
663	18072963066	刘彩霞
662	18958167819	卜智斌
688	13505817318	卢芳燕
809	13695781720	叶世伟
781	13868992616	叶向红
695	13605818530	叶小云
716	13587436160	叶晓奇
907	13588426741	吕娜
676	13857137426	吴婉英
702	13735570952	吴定英
798	13958576916	吴春龙
789	13758953542	吴海英
794	13757608695	吴燕君
774	13615758052	周尧英
690	13588758501	周权
778	13857211964	周琳
720	13626530377	周莹
772	15857353615	姚智萍
719	13587688031	孙彩霞
733	13750848040	宁丽
694	13757119617	宋剑平
736	13867134906	封亚萍
699	13588708076	庄一渝
731	13454134565	应岚
667	13588887282	张勤
745	13675851802	张国兵
808	13666550400	张岩
743	13605807800	张幸国
811	18801970460	张政
723	15957716111	张春梅
669	13957169871	张琼
805	15957823142	张登科
806	19715780258	张雪霞
738	15057145559	徐慧捷
728	13588812740	徐敏
782	15957921677	徐敏慧
673	18958066665	徐海铭
750	13426256776	徐琴鸿
758	13605772233	徐约丹
722	13758490818	徐辉
751	13605887912	戴金华
787	13758953717	方向华
674	13616555849	方玢茹
791	15657036200	方英
721	15958700544	暨玲
732	13516800991	朱健倩
761	13857271065	朱军梅
675	13958011987	朱利明
796	13958561791	朱峰
768	13750760025	朱志红
707	13606515730	朱文俊
793	13586116171	朱玲凤
770	13511332938	朱胜春
767	13586464989	朱良枫
714	13958009748	李伟
754	13857861621	李娟
730	15988193206	李娟娟
762	13819213145	李敏
759	15958762699	李格
744	15068103880	李瑾
680	13867481815	李盈
734	13777887810	李益民
803	13606698967	李雅
703	13777466804	李雅岑
756	13967880176	杜洲舸
664	18072963988	杨军
679	13758196305	杨新富
708	13757155805	杨春波
672	13754322649	杨永挺
752	13516743880	楼尉
710	13605711121	汪伟
747	13819596262	沈国
749	13957883107	沈杨
737	13606700679	洪理泉
800	13958658802	滕英
718	15268812004	潘庆霞
706	13958023308	潘永苗
804	13587179166	潘红英_丽水
700	13857188922	潘红英_邵逸夫
696	13666669123	潘胜东
681	13606507266	王临润
775	13957574797	王伟
671	15990081256	王佳峰
682	13516805833	王华芬
677	15005813026	王增
727	13588887369	王建平
713	15957110876	王晓豪
689	13958006168	王海苹
757	13676757755	王海虹
784	13566785426	王美女
786	13505899996	王跃胜
801	13566676328	王雪群
697	13757118330	田苗
810	15868899348	秦刚
711	13666650508	程晓英
765	13735100122	章兰英
792	15605701533	胡慧
661	13906537115	胡斌春
760	15905822882	胡鸿宇
725	13868414105	董爱淑
764	13735192050	蔡建利
698	13957159415	蔡斌
729	15990162166	蔡晓芳
724	13857771605	蔡雪黎
779	13957228318	袁惠萍
776	15257578280	袁铄慧
742	13758106153	诸建武
712	13588326715	诸纪华
670	13588092636	谭明明
683	13958061766	赵彩莲
686	13750880655	赵雪红
763	15805728558	邢时通
769	13732586305	郑叶平
735	13456818576	郑贝贝
783	13566781071	郭佳奕
771	13736411095	郭大为
790	13566940002	金杨君
746	18969930338	金琦
693	13757118239	金静芬
687	13588330061	钱玮
668	13738141961	钱莎莎
715	19817799771	陈俊航
726	13867702313	陈天予
795	13858600323	陈姬雅
1543	13567534846	陈志良
740	13757119185	陈昌贵
807	18957091339	陈晓红
785	13516995998	陈梦燕
691	13906535503	陈水红
797	13706760666	陈海啸
802	13567618608	陈美芬
788	13758953581	陈翔
666	13588708105	陈肖敏
701	13516820303	陈艺成
665	13357119396	陈芳
748	13957832316	陈雪琴
678	13777800601	陈静
709	13989818108	陈飞波
780	13957228260	颜波儿
685	13958111928	马楠
773	13675731188	马红丽
684	13867129329	黄丽华"""

# 另外加上刚改好的两个参赛者转评委
# 王泓权 id=453, 潘翠萍 id=455
EXTRA = [
    (453, '15867571130', '王泓权'),
    (455, '15968083640', '潘翠萍'),
]

reviewer_by_name = defaultdict(list)
for line in PROD_REVIEWER_RAW.strip().split('\n'):
    parts = line.split('\t')
    rid, rphone, rname = int(parts[0]), parts[1], parts[2]
    reviewer_by_name[rname].append((rid, rphone))
for rid, rphone, rname in EXTRA:
    reviewer_by_name[rname].append((rid, rphone))

# 特殊处理两个潘红英
panhong_shao   = next((rid for rid,p in reviewer_by_name.get('潘红英_邵逸夫',[]) ), None)
panhong_lishui = next((rid for rid,p in reviewer_by_name.get('潘红英_丽水',[])), None)

def resolve_reviewer_id(name_raw):
    """给原始名字（可能含括号）返回 reviewer_id，None=找不到"""
    if name_raw == '潘红英（邵）':
        return panhong_shao
    if name_raw == '潘红英（丽水）':
        return panhong_lishui
    base = re.sub(r'（.*?）', '', name_raw).strip()
    matches = reviewer_by_name.get(base, [])
    if len(matches) == 1:
        return matches[0][0]
    if len(matches) > 1:
        print(f"[警告] {base} 有多个账号: {matches}")
        return matches[0][0]
    return None

# ── 查DB: session_code -> [registration_id] ─────────────────
cur.execute("""
    SELECT id, final_session_code
    FROM registrations
    WHERE final_session_code IS NOT NULL AND final_session_code != ''
    ORDER BY final_session_code, final_session_order
""")
reg_rows = cur.fetchall()
regs_by_session = defaultdict(list)
for reg_id, sc in reg_rows:
    regs_by_session[sc].append(reg_id)

print(f"\n=== 各会场项目数 ===")
for sc in sorted(regs_by_session):
    print(f"  {sc}: {len(regs_by_session[sc])} 项")

# ── 检查现有 review_tasks(FINAL) 是否已有数据 ────────────────
cur.execute("SELECT COUNT(*) FROM review_tasks WHERE stage='FINAL'")
existing = cur.fetchone()[0]
print(f"\n已有 FINAL review_tasks: {existing} 条")

conn.close()

# ── 生成 INSERT SQL（用子查询动态查 registration_id，不硬编码）──
out_lines = []
out_lines.append("-- 决赛评委任务分配 review_tasks INSERT")
out_lines.append("-- 生成时间: 2026-05-31")
out_lines.append("-- 在生产库执行，registration_id 通过子查询动态获取")
out_lines.append("-- 执行前请确认 review_tasks 中 stage='FINAL' 无历史数据\n")

total_reviewers = 0
not_found_names = []

for db_code in sorted(session_experts.keys()):
    name_list = session_experts[db_code]
    out_lines.append(f"-- ── {db_code}  ({len(name_list)} 位评委) ──────────────")
    for name_raw in name_list:
        rev_id = resolve_reviewer_id(name_raw)
        if not rev_id:
            not_found_names.append(name_raw)
            out_lines.append(f"-- [未找到评委] {name_raw}")
            continue
        out_lines.append(
            f"INSERT INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)"
            f"\n  SELECT 'FINAL', r.id, {rev_id}, 'PENDING', NOW()"
            f"\n  FROM registrations r"
            f"\n  WHERE r.final_session_code = '{db_code}';"
        )
        total_reviewers += 1
    out_lines.append("")

out_path = os.path.join(base, 'scripts', 'assign_final_reviewers.sql')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))

print(f"\n=== 生成完毕 ===")
print(f"总评委-会场组合: {total_reviewers}  条（每条 INSERT...SELECT 覆盖该会场全部项目）")
if not_found_names:
    print(f"未找到评委 ({len(not_found_names)}): {not_found_names}")
print(f"输出文件: {out_path}")
