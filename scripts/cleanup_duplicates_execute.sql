-- ===========================================
-- 清理重复的材料文件记录
-- 执行时间: 2026-02-28
-- 目标: 每个报名ID + 文件类型只保留最新的一个
-- ===========================================

-- 步骤1: 备份原表（强烈建议！）
CREATE TABLE IF NOT EXISTS material_files_backup_20260228 AS 
SELECT * FROM material_files;

-- 验证备份
SELECT COUNT(*) AS backup_count FROM material_files_backup_20260228;

-- 步骤2: 查看将要删除的记录
SELECT 
    mf1.id,
    mf1.registration_id,
    mf1.type,
    mf1.file_name,
    mf1.uploaded_at,
    'TO_DELETE' AS action
FROM material_files mf1
WHERE EXISTS (
    SELECT 1 
    FROM material_files mf2 
    WHERE mf2.registration_id = mf1.registration_id 
    AND mf2.type = mf1.type 
    AND mf2.id != mf1.id
)
AND mf1.id != (
    SELECT id FROM material_files mf3
    WHERE mf3.registration_id = mf1.registration_id 
    AND mf3.type = mf1.type 
    ORDER BY uploaded_at DESC, id DESC 
    LIMIT 1
);

-- 步骤3: 执行删除（保留最新的，删除旧的）
DELETE FROM material_files
WHERE id IN (
    SELECT id FROM (
        SELECT 
            mf1.id
        FROM material_files mf1
        WHERE EXISTS (
            SELECT 1 
            FROM material_files mf2 
            WHERE mf2.registration_id = mf1.registration_id 
            AND mf2.type = mf1.type 
            AND mf2.id != mf1.id
        )
        AND mf1.id != (
            SELECT id FROM material_files mf3
            WHERE mf3.registration_id = mf1.registration_id 
            AND mf3.type = mf1.type 
            ORDER BY uploaded_at DESC, id DESC 
            LIMIT 1
        )
    ) AS duplicates
);

-- 步骤4: 验证清理结果（应该返回空结果）
SELECT 
    registration_id,
    type,
    COUNT(*) as file_count
FROM material_files
GROUP BY registration_id, type
HAVING COUNT(*) > 1;

-- 步骤5: 查看清理后的统计
SELECT 
    '清理完成' AS status,
    (SELECT COUNT(*) FROM material_files_backup_20260228) AS before_count,
    (SELECT COUNT(*) FROM material_files) AS after_count,
    (SELECT COUNT(*) FROM material_files_backup_20260228) - (SELECT COUNT(*) FROM material_files) AS deleted_count;
