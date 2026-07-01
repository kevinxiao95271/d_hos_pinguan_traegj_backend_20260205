-- 将 registrations.status='DRAFT' 的历史数据迁移到草稿表体系
-- 执行前请先运行 create_registration_drafts.sql，并做好备份
-- 匹配键：applicant_id + project_name + created_at（同申请人同时间同名视为一条）

START TRANSACTION;

INSERT INTO registration_drafts (
    competition_id, institution_id, applicant_id, project_name, group_type,
    project_leader_name, project_leader_phone, project_leader_title,
    created_at, updated_at
)
SELECT
    r.competition_id, r.institution_id, r.applicant_id, r.project_name, r.group_type,
    r.project_leader_name, r.project_leader_phone, r.project_leader_title,
    r.created_at, r.created_at
FROM registrations r
WHERE r.status = 'DRAFT';

INSERT INTO registration_draft_members (draft_id, role, name, title, department)
SELECT rd.id, rm.role, rm.name, rm.title, rm.department
FROM registration_members rm
INNER JOIN registrations r ON r.id = rm.registration_id AND r.status = 'DRAFT'
INNER JOIN registration_drafts rd
    ON rd.applicant_id = r.applicant_id
   AND rd.project_name COLLATE utf8mb4_general_ci = r.project_name COLLATE utf8mb4_general_ci
   AND rd.created_at = r.created_at;

INSERT INTO registration_draft_activity_infos (
    draft_id, theme, keywords, subject_type_code, subject_type_other,
    method_code, method_other, experience_improve_code, experience_improve_other,
    quality_topic_code, quality_topic_other, avg_work_years, avg_age,
    cross_department, related_to_digital_ai
)
SELECT
    rd.id, ai.theme, ai.keywords, ai.subject_type_code, ai.subject_type_other,
    ai.method_code, ai.method_other, ai.experience_improve_code, ai.experience_improve_other,
    ai.quality_topic_code, ai.quality_topic_other, ai.avg_work_years, ai.avg_age,
    ai.cross_department, ai.related_to_digital_ai
FROM activity_infos ai
INNER JOIN registrations r ON r.id = ai.registration_id AND r.status = 'DRAFT'
INNER JOIN registration_drafts rd
    ON rd.applicant_id = r.applicant_id
   AND rd.project_name COLLATE utf8mb4_general_ci = r.project_name COLLATE utf8mb4_general_ci
   AND rd.created_at = r.created_at;

INSERT INTO registration_draft_project_summaries (
    draft_id, theme, plan, problem, action, success, discussion, operation, presentation
)
SELECT
    rd.id, ps.theme, ps.plan, ps.problem, ps.action, ps.success, ps.discussion, ps.operation, ps.presentation
FROM project_summaries ps
INNER JOIN registrations r ON r.id = ps.registration_id AND r.status = 'DRAFT'
INNER JOIN registration_drafts rd
    ON rd.applicant_id = r.applicant_id
   AND rd.project_name COLLATE utf8mb4_general_ci = r.project_name COLLATE utf8mb4_general_ci
   AND rd.created_at = r.created_at;

INSERT INTO registration_draft_material_files (
    draft_id, type, file_name, file_url, file_hash, uploaded_at
)
SELECT
    rd.id, mf.type, mf.file_name, mf.file_url, mf.file_hash, mf.uploaded_at
FROM material_files mf
INNER JOIN registrations r ON r.id = mf.registration_id AND r.status = 'DRAFT'
INNER JOIN registration_drafts rd
    ON rd.applicant_id = r.applicant_id
   AND rd.project_name COLLATE utf8mb4_general_ci = r.project_name COLLATE utf8mb4_general_ci
   AND rd.created_at = r.created_at;

DELETE mf FROM material_files mf
INNER JOIN registrations r ON r.id = mf.registration_id AND r.status = 'DRAFT';

DELETE rm FROM registration_members rm
INNER JOIN registrations r ON r.id = rm.registration_id AND r.status = 'DRAFT';

DELETE ai FROM activity_infos ai
INNER JOIN registrations r ON r.id = ai.registration_id AND r.status = 'DRAFT';

DELETE ps FROM project_summaries ps
INNER JOIN registrations r ON r.id = ps.registration_id AND r.status = 'DRAFT';

DELETE pf FROM project_feedbacks pf
INNER JOIN registrations r ON r.id = pf.registration_id AND r.status = 'DRAFT';

DELETE FROM registrations WHERE status = 'DRAFT';

COMMIT;
