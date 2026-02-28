-- =====================================================
-- 添加外部机构支持
-- 执行时间: 2026-02-28
-- 目的: 支持评审专家来自外部机构（非医院）
-- =====================================================

-- 步骤1: 添加 is_ext 字段标识外部机构
-- 0 = 普通医院机构（默认）
-- 1 = 外部机构（卡内基、质控中心等）
ALTER TABLE institutions 
ADD COLUMN is_ext TINYINT NOT NULL DEFAULT 0 
COMMENT '是否外部机构: 0-医院, 1-外部机构';

-- 验证字段添加
SELECT COUNT(*) AS total_institutions, 
       SUM(CASE WHEN is_ext = 0 THEN 1 ELSE 0 END) AS hospital_count,
       SUM(CASE WHEN is_ext = 1 THEN 1 ELSE 0 END) AS external_count
FROM institutions;

-- 步骤2: 插入外部机构记录
-- 注意：code 和 uscc 需要唯一，使用 EXT_ 前缀避免冲突

INSERT INTO institutions (name, code, uscc, region, level, is_ext, created_at) VALUES
('卡内基', 'EXT_CARNEGIE', 'EXT000000001', '外部', '外部机构', 1, NOW()),
('浙江省护理质控中心', 'EXT_NURSING_QC', 'EXT000000002', '浙江省', '外部机构', 1, NOW()),
('浙江省质量协会', 'EXT_QUALITY_ASSOC', 'EXT000000003', '浙江省', '外部机构', 1, NOW()),
('浙江省医疗服务管理评价中心', 'EXT_MEDICAL_EVAL', 'EXT000000004', '浙江省', '外部机构', 1, NOW());

-- 步骤3: 查看插入的外部机构
SELECT 
    id,
    name,
    code,
    uscc,
    region,
    level,
    is_ext,
    created_at
FROM institutions
WHERE is_ext = 1
ORDER BY id;

-- 步骤4: 统计结果
SELECT 
    '外部机构添加完成' AS status,
    COUNT(*) AS external_institution_count
FROM institutions
WHERE is_ext = 1;

-- 步骤5: 验证所有机构统计
SELECT 
    is_ext,
    CASE WHEN is_ext = 0 THEN '医院机构' ELSE '外部机构' END AS institution_type,
    COUNT(*) AS count
FROM institutions
GROUP BY is_ext
ORDER BY is_ext;

-- =====================================================
-- 使用说明
-- =====================================================
-- 1. 创建评审专家时，可以选择这些外部机构的ID
-- 2. is_ext 字段仅作标记，代码逻辑不依赖此字段
-- 3. 前端展示时，这些外部机构和医院机构一视同仁
-- 4. 如需区分，可通过 is_ext=1 筛选外部机构
-- =====================================================
