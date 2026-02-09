#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化数据库表结构
"""

import mysql.connector

# 数据库连接配置
db_config = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# DDL语句
tables_ddl = [
    """
    CREATE TABLE IF NOT EXISTS institution (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        code VARCHAR(100),
        uscc VARCHAR(100),
        region VARCHAR(100),
        created_at DATETIME,
        INDEX idx_name (name),
        INDEX idx_uscc (uscc)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS user_account (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        phone VARCHAR(20) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        title VARCHAR(100),
        role VARCHAR(20) NOT NULL,
        institution_id BIGINT,
        reviewer_group_code VARCHAR(20),
        interview_group_code VARCHAR(20),
        expert_background VARCHAR(20),
        created_at DATETIME,
        FOREIGN KEY (institution_id) REFERENCES institution(id),
        INDEX idx_phone (phone),
        INDEX idx_role (role)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS competition (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        stage VARCHAR(20),
        created_at DATETIME,
        INDEX idx_stage (stage)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS registration (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        competition_id BIGINT NOT NULL,
        institution_id BIGINT NOT NULL,
        applicant_id BIGINT NOT NULL,
        project_name VARCHAR(255) NOT NULL,
        group_type VARCHAR(20),
        group_code VARCHAR(20),
        status VARCHAR(20),
        submitted_at DATETIME,
        approved_at DATETIME,
        created_at DATETIME,
        FOREIGN KEY (competition_id) REFERENCES competition(id),
        FOREIGN KEY (institution_id) REFERENCES institution(id),
        FOREIGN KEY (applicant_id) REFERENCES user_account(id),
        INDEX idx_competition (competition_id),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS registration_member (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        registration_id BIGINT NOT NULL,
        role VARCHAR(20) NOT NULL,
        name VARCHAR(100) NOT NULL,
        title VARCHAR(100),
        department VARCHAR(100),
        FOREIGN KEY (registration_id) REFERENCES registration(id) ON DELETE CASCADE,
        INDEX idx_registration (registration_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS activity_info (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        registration_id BIGINT NOT NULL UNIQUE,
        theme VARCHAR(255),
        keywords VARCHAR(255),
        subject_type_code VARCHAR(50),
        subject_type_other VARCHAR(255),
        method_code VARCHAR(50),
        method_other VARCHAR(255),
        experience_improve_code VARCHAR(50),
        experience_improve_other VARCHAR(255),
        quality_topic_code VARCHAR(50),
        quality_topic_other VARCHAR(255),
        avg_work_years INTEGER,
        avg_age INTEGER,
        cross_department BOOLEAN,
        FOREIGN KEY (registration_id) REFERENCES registration(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS project_summary (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        registration_id BIGINT NOT NULL UNIQUE,
        theme VARCHAR(255),
        plan TEXT,
        problem TEXT,
        action TEXT,
        success TEXT,
        discussion TEXT,
        FOREIGN KEY (registration_id) REFERENCES registration(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS material_file (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        registration_id BIGINT NOT NULL,
        file_type VARCHAR(50) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        uploaded_at DATETIME,
        FOREIGN KEY (registration_id) REFERENCES registration(id) ON DELETE CASCADE,
        INDEX idx_registration_type (registration_id, file_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS review_task (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        registration_id BIGINT NOT NULL,
        reviewer_id BIGINT NOT NULL,
        stage VARCHAR(20) NOT NULL,
        status VARCHAR(20),
        created_at DATETIME,
        FOREIGN KEY (registration_id) REFERENCES registration(id),
        FOREIGN KEY (reviewer_id) REFERENCES user_account(id),
        INDEX idx_registration (registration_id),
        INDEX idx_reviewer_stage (reviewer_id, stage),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS review_score (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        review_task_id BIGINT NOT NULL UNIQUE,
        plan INTEGER,
        problem INTEGER,
        action INTEGER,
        success INTEGER,
        review INTEGER,
        operation INTEGER,
        presentation INTEGER,
        total INTEGER,
        highlight TEXT,
        weakness TEXT,
        scored_at DATETIME,
        FOREIGN KEY (review_task_id) REFERENCES review_task(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS dictionary_item (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        type VARCHAR(50) NOT NULL,
        code VARCHAR(100) NOT NULL,
        label VARCHAR(255) NOT NULL,
        active BOOLEAN DEFAULT TRUE,
        created_at DATETIME,
        INDEX idx_type (type),
        INDEX idx_type_active (type, active),
        UNIQUE KEY uk_type_code (type, code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS system_setting (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        setting_key VARCHAR(100) NOT NULL UNIQUE,
        setting_value TEXT,
        updated_at DATETIME
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS competition_template (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        competition_id BIGINT NOT NULL,
        template_type VARCHAR(50) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        uploaded_at DATETIME,
        FOREIGN KEY (competition_id) REFERENCES competition(id) ON DELETE CASCADE,
        INDEX idx_competition_type (competition_id, template_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS activity_template (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        template_type VARCHAR(50) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        uploaded_at DATETIME,
        INDEX idx_type (template_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS institution_update_request (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        institution_id BIGINT NOT NULL,
        requester_id BIGINT NOT NULL,
        new_name VARCHAR(255),
        new_code VARCHAR(100),
        new_uscc VARCHAR(100),
        new_region VARCHAR(100),
        status VARCHAR(20),
        requested_at DATETIME,
        reviewed_at DATETIME,
        reviewer_id BIGINT,
        FOREIGN KEY (institution_id) REFERENCES institution(id),
        FOREIGN KEY (requester_id) REFERENCES user_account(id),
        FOREIGN KEY (reviewer_id) REFERENCES user_account(id),
        INDEX idx_institution (institution_id),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
]

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    print("开始创建表结构...")
    for i, ddl in enumerate(tables_ddl, 1):
        try:
            cursor.execute(ddl)
            table_name = ddl.split("TABLE")[1].split("(")[0].strip().replace("IF NOT EXISTS", "").strip("`").strip()
            print(f"  [{i}/{len(tables_ddl)}] 创建表: {table_name}")
        except Exception as e:
            print(f"  [ERROR] 创建表失败: {e}")
    
    conn.commit()
    print("\n表结构创建完成！")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"数据库操作失败: {e}")
