-- 支付凭证去重支持（material_files）
-- 规则：
-- 1) type='payment_proof' 时 file_hash 必填
-- 2) type<>'payment_proof' 时 file_hash 必须为 NULL
-- 3) payment_proof 在同一报名下按内容去重（registration_id + type + file_hash）

ALTER TABLE `material_files`
  ADD COLUMN `file_hash` VARCHAR(64) NULL COMMENT 'SHA-256 of file content';

ALTER TABLE `material_files`
  ADD UNIQUE KEY `uk_reg_type_hash` (`registration_id`, `type`, `file_hash`);

-- MySQL 8.0.16+ 才会真正执行 CHECK；低版本会解析但可能不生效
ALTER TABLE `material_files`
  ADD CONSTRAINT `chk_material_file_hash_rule`
  CHECK (
      (`type` = 'payment_proof' AND `file_hash` IS NOT NULL AND `file_hash` <> '')
      OR (`type` <> 'payment_proof' AND `file_hash` IS NULL)
  );
