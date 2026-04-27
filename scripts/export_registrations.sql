-- ============================================================
-- 2026 品管大赛 报名数据完整导出
-- 包含：报名基础信息 / 报名人手机 / 机构信息 / 活动信息 / 项目摘要 / 圈员名单
-- 用法：在 Navicat / DBeaver 等工具中直接执行，导出为 Excel/CSV
-- ============================================================

SELECT
    -- ── 报名基础信息 ──────────────────────────────────────────
    r.id                                                        AS registration_id,
    r.project_name,
    r.status,
    r.submitted_at,
    r.group_type,
    CASE r.group_type
        WHEN 'BASIC'         THEN '基层组'
        WHEN 'COMPREHENSIVE' THEN '综合组'
        WHEN 'ADVANCED'      THEN '进阶组'
        ELSE r.group_type
    END                                                         AS group_type_label,
    r.group_code,
    r.created_at,

    -- ── 报名人 ────────────────────────────────────────────────
    ua.name                                                     AS applicant_name,
    ua.phone                                                    AS applicant_phone,

    -- ── 机构信息 ──────────────────────────────────────────────
    i.name                                                      AS institution_name,
    i.level                                                     AS institution_level,
    i.uscc                                                      AS institution_uscc,
    i.region                                                    AS institution_region,
    i.city                                                      AS institution_city,

    -- ── 活动信息 ──────────────────────────────────────────────
    ai.theme                                                    AS activity_theme,
    ai.keywords,
    ai.avg_work_years,
    ai.avg_age,
    IF(ai.cross_department,      '是', '否')                   AS cross_department,
    IF(ai.related_to_digital_ai, '是', '否')                   AS related_to_digital_ai,
    ai.subject_type_code,
    d_st.label                                                  AS subject_type_label,
    ai.subject_type_other,
    ai.method_code,
    d_m.label                                                   AS method_label,
    ai.method_other,
    ai.quality_topic_code,
    d_qt.label                                                  AS quality_topic_label,
    ai.quality_topic_other,
    ai.experience_improve_code,
    d_ei.label                                                  AS experience_improve_label,
    ai.experience_improve_other,

    -- ── 项目摘要 ──────────────────────────────────────────────
    ps.theme                                                    AS summary_theme,
    ps.plan,
    ps.problem,
    ps.action,
    ps.success,
    ps.discussion,
    ps.operation,
    ps.presentation,

    -- ── 圈员名单（逗号分隔） ──────────────────────────────────
    GROUP_CONCAT(
        CASE WHEN rm.role = 'MENTOR' THEN rm.name END
        ORDER BY rm.id SEPARATOR '、'
    )                                                           AS mentor_names,
    GROUP_CONCAT(
        CASE WHEN rm.role = 'PARTICIPANT' THEN rm.name END
        ORDER BY rm.id SEPARATOR '、'
    )                                                           AS participant_names

FROM registrations r

JOIN user_accounts  ua ON ua.id = r.applicant_id
JOIN institutions    i  ON i.id  = r.institution_id
LEFT JOIN activity_infos    ai   ON ai.registration_id  = r.id
LEFT JOIN project_summaries ps   ON ps.registration_id  = r.id
LEFT JOIN registration_members rm ON rm.registration_id = r.id
-- 四个下拉框的 label 从字典表取
LEFT JOIN dictionary_items d_st ON d_st.type = 'subject_type'        AND d_st.code = ai.subject_type_code
LEFT JOIN dictionary_items d_m  ON d_m.type  = 'method'              AND d_m.code  = ai.method_code
LEFT JOIN dictionary_items d_qt ON d_qt.type = 'quality_topic'       AND d_qt.code = ai.quality_topic_code
LEFT JOIN dictionary_items d_ei ON d_ei.type = 'experience_improve'  AND d_ei.code = ai.experience_improve_code

WHERE r.competition_id = 1
  AND r.status = 'SUBMITTED'

GROUP BY
    r.id, r.project_name, r.status, r.submitted_at,
    r.group_type, r.group_code, r.created_at,
    ua.name, ua.phone,
    i.name, i.level, i.uscc, i.region, i.city,
    ai.theme, ai.keywords, ai.avg_work_years, ai.avg_age,
    ai.cross_department, ai.related_to_digital_ai,
    ai.subject_type_code, d_st.label, ai.subject_type_other,
    ai.method_code, d_m.label, ai.method_other,
    ai.quality_topic_code, d_qt.label, ai.quality_topic_other,
    ai.experience_improve_code, d_ei.label, ai.experience_improve_other,
    ps.theme, ps.plan, ps.problem, ps.action,
    ps.success, ps.discussion, ps.operation, ps.presentation

ORDER BY r.id;
