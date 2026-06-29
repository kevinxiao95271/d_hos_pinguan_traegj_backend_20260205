import pymysql, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from collections import defaultdict

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606, user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

# 分配表里的全部专家名
assign_names_raw = [
    '陈水红','郭佳奕','朱良枫','潘红英（邵）','陈昌贵',
    '赵彩莲','陈志良','王泓权','方玢茹',
    '马红丽','张国兵','袁惠萍','胡慧',
    '杨永挺','俞雪芬','洪理泉','吴定英',
    '周权','黄丽华','徐敏慧','郑叶平',
    '谭明明','刘彩霞','吕娜','吴春龙',
    '陈雪琴','王建平','宋剑平','章兰英',
    '李盈','冯志仙','胡鸿宇','宁丽','徐辉',
    '应岚','潘庆霞','朱军梅','朱胜春',
    '程晓英','周莹','吴燕君','叶世伟',
    '丁志明','王海虹','郭大为','叶小云',
    '王临润','卜智斌','潘红英（丽水）','冯素文',
    '朱文俊','朱志红','蔡建利','冯少为',
    '蔡晓芳','陈肖敏','袁铄慧','张雪霞',
    '王跃胜','蔡斌','张春梅','李雅','吴婉英',
    '杨军','楼尉','沈国','钱玮',
    '方英','陈梦燕','陈美芬','徐约丹',
    '孙彩霞','杜洲舸','张幸国','封亚萍',
    '潘翠萍','吴海英','刘仁杰','李益民',
    '朱健倩','马楠','姚智萍','周尧英','汪伟',
    '杨新富','滕英','周琳','张琼',
]

# 去括号，得纯名字
base_names = list({re.sub(r'（.*?）', '', n).strip() for n in assign_names_raw})

# 查DB中REVIEWER账号
placeholders = ','.join(['%s'] * len(base_names))
cur.execute(f"""
    SELECT ua.name, ua.phone, i.name AS institution
    FROM user_accounts ua
    LEFT JOIN institutions i ON i.id = ua.institution_id
    WHERE ua.role = 'REVIEWER'
      AND ua.name IN ({placeholders})
    ORDER BY ua.name
""", base_names)
rows = cur.fetchall()
conn.close()

by_name = defaultdict(list)
for name, phone, inst in rows:
    by_name[name].append((phone, inst))

print(f"DB中共匹配到 {len(rows)} 条 REVIEWER 记录\n")

print("=== 重名（DB中同名多人）===")
found_dup = False
for name, persons in sorted(by_name.items()):
    if len(persons) > 1:
        found_dup = True
        print(f"[重名] {name}  ({len(persons)}人):")
        for phone, inst in persons:
            print(f"         {phone}  {inst}")

if not found_dup:
    print("无重名")

print("\n=== 未在DB中找到 ===")
not_found = []
for raw in assign_names_raw:
    base = re.sub(r'（.*?）', '', raw).strip()
    if base not in by_name:
        not_found.append(raw)
if not_found:
    for n in not_found:
        print(f"  {n}")
else:
    print("全部找到")
