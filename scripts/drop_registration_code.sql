-- 删除 registrations 表中的 registration_code 列（死字段，全为 null，从未在生产中使用）
-- 测试库与生产库均可执行（先确认全部为 NULL 再执行）

-- 确认前先查一下，确保全为 NULL
-- SELECT COUNT(*) FROM registrations WHERE registration_code IS NOT NULL;

ALTER TABLE registrations DROP COLUMN IF EXISTS registration_code;
