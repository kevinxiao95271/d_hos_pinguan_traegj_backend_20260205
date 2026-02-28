-- ============================================
-- 系统模版文件表
-- ============================================

CREATE TABLE system_template_files (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    template_type VARCHAR(64) NOT NULL COMMENT '模版类型: registration_form(报名表), result_report(成果报告)',
    file_name VARCHAR(200) NOT NULL COMMENT '原始文件名',
    minio_object_name VARCHAR(300) NOT NULL COMMENT 'MinIO对象名称（路径）',
    file_size BIGINT NOT NULL COMMENT '文件大小(字节)',
    version INT NOT NULL DEFAULT 1 COMMENT '版本号',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否当前激活版本',
    uploaded_by BIGINT COMMENT '上传人用户ID',
    uploaded_at DATETIME NOT NULL COMMENT '上传时间',
    description VARCHAR(500) COMMENT '描述信息',
    
    CONSTRAINT fk_uploaded_by FOREIGN KEY (uploaded_by) REFERENCES user_accounts(id),
    INDEX idx_template_type (template_type),
    INDEX idx_is_active (is_active),
    INDEX idx_type_active (template_type, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统模版文件表';
