import pymysql

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4',
    connect_timeout=15
)
cur = conn.cursor()

ddl = """
CREATE TABLE IF NOT EXISTS `deadline_exemptions` (
  `id`              BIGINT       NOT NULL AUTO_INCREMENT,
  `competition_id`  BIGINT       NOT NULL COMMENT '所属赛事ID',
  `registration_id` BIGINT       NOT NULL COMMENT '豁免的报名项目ID',
  `expire_at`       DATETIME     NOT NULL COMMENT '豁免到期时间，过期自动失效',
  `remark`          VARCHAR(200)          COMMENT '备注',
  `created_at`      DATETIME     NOT NULL,
  `updated_at`      DATETIME     NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_comp_registration` (`competition_id`, `registration_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='截止时间豁免记录（报名项目级别）'
"""

cur.execute(ddl)
conn.commit()
print("deadline_exemptions table created OK")

cur.execute("SHOW TABLES LIKE 'deadline_exemptions'")
print("verify:", cur.fetchone())

cur.close()
conn.close()
