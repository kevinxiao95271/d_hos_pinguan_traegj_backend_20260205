"""
生成专家账号批量 INSERT SQL
- role = REVIEWER
- 随机8位字母+数字密码，bcrypt加密
- institution_id 用子查询按 uscc 匹配，不硬编码 id
- 跳过重复手机号的专家
"""
import pandas as pd
import bcrypt
import random
import string
import json
import re

# ── 机构名 → USCC 映射（含别名对齐）──────────────────────────────────────────
INST_USCC = {
    # 已存在
    '丽水市人民医院':             '12332500472310648J',
    '义乌市中心医院':             '12330782471771856W',
    '杭州市第二人民医院':         '12330100470116622A',  # = 杭州师范大学附属医院
    '杭州师范大学附属医院':       '12330100470116622A',
    '温州市人民医院':             '123303004705255657',
    '宁波市鄞州第二医院':         '12330227756286168R',  # = 宁波市中西医结合医院
    '宁波市中西医结合医院':       '12330227756286168R',
    # 新插入
    '台州市第一人民医院':         '12331003472690185U',
    '浙江中医药大学附属第二医院': '12330000470032824N',
    '浙江省立同德医院':           '12330000470051793D',
    '瑞安市人民医院':             '12330381470860064L',
    '萧山区第一人民医院':         '12330109470453493C',
    '杭州市萧山区第一人民医院':   '12330109470453493C',
    '杭州市红会医院':             '12330100470116657W',
    '杭州市红十字会医院':         '12330100470116657W',
    '树兰(安吉)医院':             '91330523MA28CUHJ9B',
    '树兰（安吉）医院':           '91330523MA28CUHJ9B',
    # EXT 机构
    '省医管中心':                 'EXT000000005',
    '浙江省医院管理中心':         'EXT000000005',
    '浙江大学':                   'EXT000000006',
    '浙江省质量协会':             'EXT000000003',
}

# 读之前通过 eval_inst_match.py 分析出来的完整机构映射 ─ 直接把 init_prod 里已有的也补进来
# 这里列出新文件里出现的所有机构名，按前期分析补全
EXTRA_USCC = {
    '浙江大学医学院附属第一医院':     '12330000470019360B',
    '浙江大学医学院附属第二医院':     '12330000470019376C',
    '浙江大学医学院附属邵逸夫医院':   '12330000470019424F',
    '浙江大学医学院附属妇产科医院':   '12330000470019389U',
    '浙江大学医学院附属儿童医院':     '12330000470019428J',
    '浙江大学医学院附属第四医院':     '12330782689145495P',
    '浙江大学医学院附属口腔医院':     '12330000470003281H',
    '浙江省人民医院':                 '12330000470019406W',
    '浙江省肿瘤医院':                 '12330000MA27YJY25A',
    '浙江省中医院':                   '12330000470019413U',
    '浙江省儿童医院':                 '12330000470019428J',
    '浙江医院':                       '12330000470051734A',
    '杭州市第一人民医院':             '12330100470116641B',
    '杭州市第三人民医院':             '12330100470116636Y',
    '杭州市第七人民医院':             '12330100470116673J',
    '杭州市儿童医院':                 '12330100470116643F',
    '杭州市肿瘤医院':                 '12330100470116639X',
    '杭州市中医院':                   '12330100470116637C',
    '杭州市妇产科医院':               '12330100470116645J',
    '树兰（杭州）医院':               '91330100321916626N',
    '宁波市第一医院':                 '12330200470116670E',
    '宁波市第二医院':                 '12330200470116671Y',
    '宁波市医疗中心李惠利医院':       '1233020041952986XM',
    '宁波医疗中心李惠利医院':         '1233020041952986XM',
    '宁波市李惠利医院':               '1233020041952986XM',
    '宁波大学附属第一医院':           '12330200470116670E',
    '宁波大学附属人民医院':           '12330227419611919D',
    '宁波市第九医院':                 '12330205419550546R',
    '温州医科大学附属第一医院':       '12330300470116760K',
    '温州医科大学附属第二医院':       '12330300470116762P',
    '温州医科大学附属眼视光医院':     '12330300470116764U',
    '温州市中心医院':                 '12330300470525557C',
    '嘉兴市第一医院':                 '12330400470460526N',
    '嘉兴市第二医院':                 '12330400470460530E',
    '嘉兴市中医院':                   '12330400470890693Q',
    '嘉兴市中医医院':                 '12330400470890693Q',
    '湖州市中心医院':                 '12330500470460574F',
    '湖州市第一人民医院':             '12330500470460574F',
    '绍兴市人民医院':                 '12330600470460618K',
    '绍兴市中心医院':                 '12330600470460619E',
    '诸暨市人民医院':                 '12330681471481007R',
    '金华市中心医院':                 '12330700470460651T',
    '金华市人民医院':                 '12330700470460652N',
    '东阳市人民医院':                 '1233078347180163XH',
    '衢州市人民医院':                 '12330800470460676T',
    '衢州市柯城区人民医院':           '12330802470460721J',
    '舟山医院':                       '12330900472092185H',
    '舟山市人民医院':                 '12330900470460697X',
    '台州市中心医院':                 '12331000470460720G',
    '台州恩泽医疗中心（集团）':       '12331000470460721A',
    '浙江省台州医院':                 '12331000796490606H',
    '温岭市第一人民医院':             '123310817458062608',
    '丽水市中心医院':                 '12332500470460767T',
    '丽水市第二人民医院':             '12332500472260070Y',
    '宁波市鄞州人民医院':             '12330212470460460T',
    '余杭区第一人民医院':             '12330110470453521G',
    '富阳区第一人民医院':             '12330111470453567P',
}
INST_USCC.update(EXTRA_USCC)

def random_password(length=8):
    chars = string.ascii_letters + string.digits
    while True:
        pwd = ''.join(random.choices(chars, k=length))
        # 保证至少含1字母1数字
        if re.search(r'[a-zA-Z]', pwd) and re.search(r'\d', pwd):
            return pwd

def bcrypt_hash(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')

# ── 读新专家文件 ─────────────────────────────────────────────────────────────
# 第1行（index=0）是标题行，第2行（index=1）才是列头
df = pd.read_excel('浙江省品管大赛专家库成员名单(2025.5.22更新).xlsx', dtype=str, header=1)
df.columns = df.columns.str.strip()
# 列名: 单位 专家 专业 专业背景 职务 联系方式
df.rename(columns={'专家': '姓名', '联系方式': '手机'}, inplace=True)
df = df.dropna(subset=['姓名', '手机'])
df['手机'] = df['手机'].str.strip()
df['姓名'] = df['姓名'].str.strip()
# 去掉单元格内换行符（如"浙江大学医学院附属\n第一医院"）
df['单位'] = df['单位'].str.replace(r'\s+', '', regex=True)

# ── 找重复手机号，全部忽略 ──────────────────────────────────────────────────
dup_phones = set(df[df.duplicated('手机', keep=False)]['手机'].tolist())
print(f'重复手机号（忽略）: {len(dup_phones)} 个，涉及专家 {len(df[df["手机"].isin(dup_phones)])} 人')
df_clean = df[~df['手机'].isin(dup_phones)].copy()
print(f'有效专家数: {len(df_clean)}')

# ── 生成 SQL ─────────────────────────────────────────────────────────────────
rows = []
skipped = []
pwd_records = []

for _, row in df_clean.iterrows():
    inst_name = row.get('单位', '').strip()
    expert_name = row.get('姓名', '').strip()
    phone = row.get('手机', '').strip()
    background = row.get('专业背景', '') or ''
    background = str(background).strip() if background != 'nan' else ''

    uscc = INST_USCC.get(inst_name)
    if not uscc:
        skipped.append({'name': expert_name, 'inst': inst_name, 'phone': phone})
        continue

    pwd_plain = random_password()
    pwd_hash = bcrypt_hash(pwd_plain)
    pwd_records.append({'name': expert_name, 'phone': phone, 'password': pwd_plain})

    # background 截断到32字符
    bg_val = background[:32] if background else ''
    bg_sql = f"'{bg_val}'" if bg_val else 'NULL'

    sql = (
        f"INSERT INTO `user_accounts` (`name`, `phone`, `password`, `role`, `institution_id`, `expert_background`, `enabled`, `created_at`) "
        f"VALUES ("
        f"'{expert_name}', "
        f"'{phone}', "
        f"'{pwd_hash}', "
        f"'REVIEWER', "
        f"(SELECT id FROM institutions WHERE uscc = '{uscc}' LIMIT 1), "
        f"{bg_sql}, "
        f"1, "
        f"NOW()"
        f");"
    )
    rows.append(sql)

# 输出 SQL 文件
with open('scripts/insert_experts.sql', 'w', encoding='utf-8') as f:
    f.write('-- 清除旧的 REVIEWER 账号（仅测试库执行，生产库删除此行）\n')
    f.write("-- DELETE FROM user_accounts WHERE role = 'REVIEWER';\n\n")
    f.write(f'-- 共 {len(rows)} 条专家记录\n\n')
    for s in rows:
        f.write(s + '\n')

# 输出明文密码记录（本地留存，不提交）
with open('scripts/expert_passwords.json', 'w', encoding='utf-8') as f:
    json.dump(pwd_records, f, ensure_ascii=False, indent=2)

result = {
    'generated': len(rows),
    'skipped': len(skipped),
    'skipped_detail': skipped,
    'dup_phones_count': len(dup_phones),
}
with open('scripts/gen_expert_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
