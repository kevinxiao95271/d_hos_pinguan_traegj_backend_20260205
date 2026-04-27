-- system_settings 初始化（导出自当前环境）
START TRANSACTION;

INSERT INTO system_settings (setting_key, setting_value, updated_at) VALUES
('advancedGroupCount', '25', NOW()),
('basicGroupCount', '25', NOW()),
('comprehensiveGroupCount', '25', NOW()),
('currentCompetitionId', '1', NOW()),
('maxRegistrationsPerInstitution', '8', NOW()),
('reviewerMaxLoad', '15', NOW()),
('shortlistRatio', '0.3', NOW())
ON DUPLICATE KEY UPDATE
setting_value = VALUES(setting_value),
updated_at = NOW();

COMMIT;
