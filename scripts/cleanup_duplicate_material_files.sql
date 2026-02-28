-- 检查和清理重复的材料文件记录
-- 每个报名ID + 文件类型(type) 只保留最新的一个

-- 1. 查看重复情况统计
SELECT 
    '=== 重复文件统计 ===' AS info;

SELECT 
    registration_id,
    type,
    COUNT(*) as file_count,
    MIN(uploaded_at) as earliest_upload,
    MAX(uploaded_at) as latest_upload,
    GROUP_CONCAT(id ORDER BY id) as file_ids
FROM material_files
GROUP BY registration_id, type
HAVING COUNT(*) > 1
ORDER BY file_count DESC, registration_id, type;

-- 2. 详细查看重复记录
SELECT 
    '=== 重复记录详细信息 ===' AS info;

SELECT 
    mf1.id,
    mf1.registration_id,
    mf1.type,
    mf1.file_name,
    mf1.file_url,
    mf1.uploaded_at,
    CASE 
        WHEN mf1.id = (
            SELECT id FROM material_files mf2 
            WHERE mf2.registration_id = mf1.registration_id 
            AND mf2.type = mf1.type 
            ORDER BY uploaded_at DESC, id DESC 
            LIMIT 1
        ) THEN '保留(最新)'
        ELSE '删除(旧文件)'
    END AS action
FROM material_files mf1
WHERE EXISTS (
    SELECT 1 
    FROM material_files mf2 
    WHERE mf2.registration_id = mf1.registration_id 
    AND mf2.type = mf1.type 
    AND mf2.id != mf1.id
)
ORDER BY mf1.registration_id, mf1.type, mf1.uploaded_at DESC;

-- 3. 统计需要删除的文件数量
SELECT 
    '=== 清理统计 ===' AS info;

SELECT 
    COUNT(*) as total_duplicate_files,
    COUNT(DISTINCT registration_id) as affected_registrations,
    COUNT(DISTINCT type) as affected_types
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

-- 4. 按type统计重复情况
SELECT 
    '=== 按文件类型统计 ===' AS info;

SELECT 
    type,
    COUNT(*) as duplicate_count,
    COUNT(DISTINCT registration_id) as registrations_affected
FROM material_files mf1
WHERE EXISTS (
    SELECT 1 
    FROM material_files mf2 
    WHERE mf2.registration_id = mf1.registration_id 
    AND mf2.type = mf1.type 
    AND mf2.id != mf1.id
)
GROUP BY type;

-- ===============================================
-- 5. 清理操作（慎重执行！建议先备份）
-- ===============================================
-- 注意：以下DELETE语句默认被注释，请确认无误后再执行

-- 备份建议：
-- CREATE TABLE material_files_backup_20260228 AS SELECT * FROM material_files;

-- 删除重复记录，只保留最新的
/*
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
*/

-- 6. 验证清理结果
SELECT 
    '=== 清理后验证 ===' AS info;

SELECT 
    registration_id,
    type,
    COUNT(*) as file_count
FROM material_files
GROUP BY registration_id, type
HAVING COUNT(*) > 1;

-- 如果上面查询无结果，说明清理成功
