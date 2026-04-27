import pymysql

conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    database="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4",
)

stmts = [
    "ALTER TABLE `material_files` ADD COLUMN `file_hash` VARCHAR(64) NULL COMMENT 'SHA-256 of file content'",
    "ALTER TABLE `material_files` ADD UNIQUE KEY `uk_reg_type_hash` (`registration_id`, `type`, `file_hash`)",
    """ALTER TABLE `material_files`
       ADD CONSTRAINT `chk_material_file_hash_rule`
       CHECK (
          (`type` = 'payment_proof' AND `file_hash` IS NOT NULL AND `file_hash` <> '')
          OR (`type` <> 'payment_proof' AND `file_hash` IS NULL)
       )""",
]

try:
    with conn.cursor() as cur:
        for s in stmts:
            try:
                cur.execute(s)
                print("OK:", s.split()[2], s[:60])
            except Exception as e:
                msg = str(e)
                if "Duplicate column name" in msg or "Duplicate key name" in msg or "Duplicate check constraint name" in msg:
                    print("SKIP:", msg)
                else:
                    raise
    conn.commit()
    print("Migration done.")
finally:
    conn.close()
