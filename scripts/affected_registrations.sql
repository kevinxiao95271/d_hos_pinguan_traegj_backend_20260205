-- 鍏?1497 涓猆SCC锛堝悓USCC澶氬悕绉帮級

-- ================================================
-- 鏌ュ摢浜涙姤鍚嶉」鐩惤鍦ㄨ繖浜涙満鏋勮寖鍥村唴
-- ================================================
SELECT
    r.id            AS registration_id,
    r.project_name,
    r.group_type,
    r.status,
    r.submitted_at,
    i.id            AS institution_id,
    i.name          AS institution_name,
    i.uscc,
    ua.id           AS user_id,
    ua.phone,
    ua.name         AS user_name
FROM registrations r
JOIN institutions i  ON r.institution_id = i.id
JOIN user_accounts ua ON r.applicant_id  = ua.id
WHERE i.uscc IN (
    SELECT uscc FROM const_init_institutions
    WHERE uscc IS NOT NULL
    GROUP BY uscc
    HAVING COUNT(DISTINCT name) > 1
)
ORDER BY i.uscc, r.id;
