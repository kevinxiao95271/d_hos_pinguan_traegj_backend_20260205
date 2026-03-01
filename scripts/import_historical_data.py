"""
历史数据导入脚本
将 2024年度 和 2025年度 历史数据 Excel 导入 pinguan_his_data 表
"""
import xlrd
import pymysql
import sys

# ── 数据库配置 ──────────────────────────────────────────────
DB_CONFIG = {
    "host":   "gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    "port":   63606,
    "user":   "root",
    "password": "Yiguo9527_",
    "database": "d_hos_pinguan_traegj_20260205",
    "charset": "utf8mb4",
}

# ── 要导入的文件 ────────────────────────────────────────────
FILES = [
    "2024年度-历史数据_20260207.xls",
    "2025年度-历史数据_20260207.xls",
]

INSERT_SQL = """
INSERT INTO pinguan_his_data (
    data_status, input_person, input_date, year,
    group_name, project_code, competition_group, project_name,
    institution_name, institution_level, institution_address, total_beds,
    hospital_contact_name, hospital_contact_title, hospital_contact_phone, hospital_contact_email,
    project_leader_name, project_leader_title, project_leader_phone, project_leader_email,
    circle_name
) VALUES (
    %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s
)
"""

def cell_to_str(cell):
    """将 xlrd 单元格值统一转为字符串，空值返回 None"""
    if cell.ctype == xlrd.XL_CELL_EMPTY:
        return None
    if cell.ctype == xlrd.XL_CELL_NUMBER:
        v = cell.value
        # 整数型数字去掉小数点（如 2024.0 -> "2024"）
        return str(int(v)) if v == int(v) else str(v)
    return str(cell.value).strip() or None


def import_file(conn, filepath):
    print(f"\n>>> 正在导入: {filepath}")
    wb = xlrd.open_workbook(filepath, encoding_override="gbk")
    ws = wb.sheet_by_index(0)

    total = ws.nrows - 1  # 去掉表头行
    print(f"    数据行数: {total}")

    rows = []
    for i in range(1, ws.nrows):
        row = ws.row(i)
        values = tuple(cell_to_str(c) for c in row)
        rows.append(values)

    cursor = conn.cursor()
    cursor.executemany(INSERT_SQL, rows)
    conn.commit()
    print(f"    导入成功: {cursor.rowcount} 行")
    cursor.close()


def main():
    print("连接数据库...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"连接失败: {e}")
        sys.exit(1)

    # 导入前先查一下现有数量
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pinguan_his_data")
    existing = cursor.fetchone()[0]
    cursor.close()
    print(f"当前表中已有 {existing} 条记录")

    if existing > 0:
        answer = input("表中已有数据，是否清空后重新导入？(y/N): ").strip().lower()
        if answer == "y":
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE pinguan_his_data")
            conn.commit()
            cursor.close()
            print("已清空表")
        else:
            print("追加模式，保留现有数据")

    for f in FILES:
        import_file(conn, f)

    # 汇总
    cursor = conn.cursor()
    cursor.execute("SELECT year, COUNT(*) FROM pinguan_his_data GROUP BY year ORDER BY year")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    print("\n=== 导入完成 ===")
    total = 0
    for year, cnt in rows:
        print(f"  {year} 年度: {cnt} 条")
        total += cnt
    print(f"  合计: {total} 条")


if __name__ == "__main__":
    main()
