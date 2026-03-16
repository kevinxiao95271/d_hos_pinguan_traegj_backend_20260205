-- 截止时间豁免表（报名项目级别）
-- 允许 OPS / COMMITTEE_ADMIN 为指定报名项目开绿灯，在豁免期内可越过报名截止时间提交
CREATE TABLE IF NOT EXISTS `deadline_exemptions` (
  `id`              BIGINT       NOT NULL AUTO_INCREMENT,
  `competition_id`  BIGINT       NOT NULL COMMENT '所属赛事ID',
  `registration_id` BIGINT       NOT NULL COMMENT '豁免的报名项目ID',
  `expire_at`       DATETIME     NOT NULL COMMENT '豁免到期时间，过期自动失效',
  `remark`          VARCHAR(200)          COMMENT '备注，如批准人、原因',
  `created_at`      DATETIME     NOT NULL,
  `updated_at`      DATETIME     NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_comp_registration` (`competition_id`, `registration_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='截止时间豁免记录（报名项目级别）';
