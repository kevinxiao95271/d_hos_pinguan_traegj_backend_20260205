-- 查询 activity_infos 相关字段用到的 dictionary_items codes
-- （用于核对下面 INSERT 语句里的 code 值是否正确）

-- 1. 查看所有 activity_infos 相关的字典类型
SELECT DISTINCT type FROM dictionary_items
WHERE type LIKE '%subject%' OR type LIKE '%method%' OR type LIKE '%quality%' OR type LIKE '%experience%' OR type LIKE '%activity%'
ORDER BY type;

-- 2. 查看现有 activity_infos 里用到的 codes（对照已有数据）
SELECT DISTINCT
    subject_type_code,
    method_code,
    quality_topic_code,
    experience_improve_code
FROM activity_infos
WHERE subject_type_code IS NOT NULL
LIMIT 10;

-- 3. 查出字典表里所有主题类型的label和code
SELECT type, code, label FROM dictionary_items
WHERE type IN (
    SELECT DISTINCT type FROM dictionary_items
    WHERE label IN ('医疗质量与安全','病人照护','成本效益','教育训练','流程改造','医疗信息')
)
ORDER BY type, sort_order;
