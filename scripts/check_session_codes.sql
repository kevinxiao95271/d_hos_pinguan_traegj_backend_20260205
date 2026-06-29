-- 查当前所有 final_session_code 值
SELECT DISTINCT final_session_code, COUNT(*) AS cnt
FROM registrations
WHERE final_session_code IS NOT NULL
GROUP BY final_session_code
ORDER BY final_session_code;
