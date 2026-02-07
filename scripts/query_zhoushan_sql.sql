-- 查询舟山医院
SELECT 
    id,
    name AS 机构名称,
    code AS 机构代码,
    uscc AS 统一社会信用代码,
    region AS 地区,
    level AS 等级,
    created_at AS 创建时间
FROM institutions
WHERE name LIKE '%舟山%'
ORDER BY id;

-- 查询舟山医院的报名项目
SELECT 
    r.id,
    r.project_name AS 项目名称,
    r.group_type AS 组别,
    r.group_code AS 分组,
    r.status AS 状态,
    r.submitted_at AS 提交时间,
    u.name AS 负责人,
    i.name AS 机构名称
FROM registrations r
LEFT JOIN user_accounts u ON r.applicant_id = u.id
LEFT JOIN institutions i ON r.institution_id = i.id
WHERE i.name LIKE '%舟山%'
ORDER BY r.id;
