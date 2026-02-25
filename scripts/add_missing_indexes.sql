-- 添加缺失的索引以提升性能
-- 这些索引对报名流程至关重要

-- 1. user_accounts表的institution_id索引
CREATE INDEX idx_institution_id ON user_accounts(institution_id);

-- 2. registrations表的institution_id索引
CREATE INDEX idx_institution_id ON registrations(institution_id);

-- 3. registrations表的applicant_id索引
CREATE INDEX idx_applicant_id ON registrations(applicant_id);

-- 4. 其他可能需要的索引
CREATE INDEX idx_competition_id ON registrations(competition_id);
CREATE INDEX idx_status ON registrations(status);
CREATE INDEX idx_group_code ON registrations(group_code);

-- 5. user_accounts其他索引
CREATE INDEX idx_role ON user_accounts(role);
CREATE INDEX idx_enabled ON user_accounts(enabled);

-- 查看索引创建结果
SHOW INDEX FROM user_accounts;
SHOW INDEX FROM registrations;
