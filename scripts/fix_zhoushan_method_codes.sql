-- 修正舟山医院项目的methodCode
-- 将无效的code改为系统中已存在的有效code

-- 1. qcc -> qc_topic (品管圈-课题达成)
UPDATE activity_infos 
SET method_code = 'qc_topic'
WHERE method_code = 'qcc'
  AND registration_id IN (
    SELECT id FROM registrations 
    WHERE institution_id = (SELECT id FROM institutions WHERE name = '舟山医院')
  );

-- 2. benchmarking -> method_7 (标杆学习)
UPDATE activity_infos 
SET method_code = 'method_7'
WHERE method_code = 'benchmarking'
  AND registration_id IN (
    SELECT id FROM registrations 
    WHERE institution_id = (SELECT id FROM institutions WHERE name = '舟山医院')
  );

-- 3. process_reengineering -> process_improve (流程改造)
UPDATE activity_infos 
SET method_code = 'process_improve'
WHERE method_code = 'process_reengineering'
  AND registration_id IN (
    SELECT id FROM registrations 
    WHERE institution_id = (SELECT id FROM institutions WHERE name = '舟山医院')
  );

-- 4. system_construct -> process_improve (流程改造)
UPDATE activity_infos 
SET method_code = 'process_improve'
WHERE method_code = 'system_construct'
  AND registration_id IN (
    SELECT id FROM registrations 
    WHERE institution_id = (SELECT id FROM institutions WHERE name = '舟山医院')
  );

-- 查询修改结果
SELECT 
    r.id as registration_id,
    r.project_name,
    a.method_code,
    '修改完成' as status
FROM registrations r
LEFT JOIN activity_infos a ON a.registration_id = r.id
WHERE r.institution_id = (SELECT id FROM institutions WHERE name = '舟山医院')
ORDER BY r.id;
