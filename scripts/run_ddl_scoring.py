import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205', charset='utf8mb4'
)
cur = conn.cursor()

ddls = [
    ("interview_scores", """
CREATE TABLE IF NOT EXISTS `interview_scores` (
  `id`             bigint       NOT NULL AUTO_INCREMENT,
  `review_task_id` bigint       NOT NULL,
  `topic`          double       NOT NULL DEFAULT 0,
  `process`        double       NOT NULL DEFAULT 0,
  `operation`      double       NOT NULL DEFAULT 0,
  `result`         double       NOT NULL DEFAULT 0,
  `total`          double       NOT NULL DEFAULT 0,
  `highlight`      varchar(500) DEFAULT NULL,
  `weakness`       varchar(500) DEFAULT NULL,
  `submitted_at`   datetime(6)  NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_review_task_id` (`review_task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
"""),
    ("scoring_snapshots", """
CREATE TABLE IF NOT EXISTS `scoring_snapshots` (
  `id`              bigint      NOT NULL AUTO_INCREMENT,
  `competition_id`  bigint      NOT NULL,
  `registration_id` bigint      NOT NULL,
  `stage`           varchar(32) NOT NULL,
  `group_code`      varchar(64) DEFAULT NULL,
  `group_type`      varchar(32) NOT NULL,
  `raw_avg`         double      DEFAULT NULL,
  `group_avg`       double      DEFAULT NULL,
  `overall_avg`     double      DEFAULT NULL,
  `coefficient`     double      DEFAULT NULL,
  `adjusted_score`  double      DEFAULT NULL,
  `irank`           int         DEFAULT NULL,
  `calculated_at`   datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_reg_stage` (`registration_id`, `stage`),
  KEY `idx_competition_stage` (`competition_id`, `stage`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
"""),
    ("registrations shortlist columns", """
ALTER TABLE `registrations`
  ADD COLUMN IF NOT EXISTS `shortlist_override` varchar(16)  DEFAULT NULL COMMENT 'INCLUDE/EXCLUDE',
  ADD COLUMN IF NOT EXISTS `shortlist_note`     varchar(200) DEFAULT NULL COMMENT '人工干预说明'
"""),
]

for name, sql in ddls:
    try:
        cur.execute(sql)
        conn.commit()
        print(f'[OK] {name}')
    except Exception as e:
        print(f'[ERR] {name}: {e}')

# 验证
print('\n=== 验证 ===')
for t in ['interview_scores', 'scoring_snapshots']:
    cur.execute(f'SELECT COUNT(*) FROM {t}')
    print(f'{t}: {cur.fetchone()[0]} rows')

cur.execute("SHOW COLUMNS FROM registrations LIKE 'shortlist%'")
cols = cur.fetchall()
for c in cols:
    print(f'registrations.{c[0]}: {c[1]}')

conn.close()
