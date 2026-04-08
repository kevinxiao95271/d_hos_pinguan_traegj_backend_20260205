package com.trae.pinguan.config;

import com.trae.pinguan.repository.SystemSettingRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class DataSourceInitializer implements ApplicationRunner {
    private final SystemSettingRepository systemSettingRepository;
    private final JdbcTemplate jdbcTemplate;

    @Override
    public void run(ApplicationArguments args) {
        systemSettingRepository.findBySettingKey("activeDataSource")
                .ifPresent(setting -> DataSourceContext.setCurrent(setting.getSettingValue()));
        ensureColumn("user_accounts", "reviewer_group_code", "varchar(32)");
        ensureColumn("user_accounts", "interview_group_code", "varchar(32)");
        ensureColumn("user_accounts", "expert_background", "varchar(32)");
        ensureColumn("user_accounts", "notice_confirmed_at", "DATETIME(6)");
        ensureReviewerProfilesTable();
        ensureColumn("reviewer_profiles", "department", "varchar(64)");
        ensureColumn("reviewer_profiles", "backgrounds_other", "varchar(255)");
        ensureColumn("reviewer_profiles", "tools_other", "varchar(255)");
        ensureColumn("reviewer_profiles", "topics_other", "varchar(255)");
        ensureColumn("review_tasks", "recuse_reason_code", "varchar(64)");
        ensureColumn("review_tasks", "recuse_reason_other", "varchar(255)");
        ensureReviewerInstitutionChangesTable();
        ensureRecuseReasonDictionary();
        ensureScoreColumnsNullable();
    }

    private void ensureColumn(String tableName, String columnName, String definition) {
        // 使用DATABASE()函数，MySQL和PostgreSQL都支持（在PostgreSQL中是CURRENT_DATABASE()）
        Integer count = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=? AND COLUMN_NAME=?",
                Integer.class,
                tableName,
                columnName
        );
        if (count != null && count == 0) {
            jdbcTemplate.execute("ALTER TABLE " + tableName + " ADD COLUMN " + columnName + " " + definition);
        }
    }

    /**
     * 草稿保存功能要求评分字段可为 NULL（旧表建时是 NOT NULL）。
     * 用 MODIFY COLUMN 幂等地将相关列改为 NULL。
     */
    private void ensureScoreColumnsNullable() {
        // review_scores
        modifyColumnNullable("review_scores", "plan",         "DOUBLE");
        modifyColumnNullable("review_scores", "problem",      "DOUBLE");
        modifyColumnNullable("review_scores", "action",       "DOUBLE");
        modifyColumnNullable("review_scores", "success",      "DOUBLE");
        modifyColumnNullable("review_scores", "review",       "DOUBLE");
        modifyColumnNullable("review_scores", "operation",    "DOUBLE");
        modifyColumnNullable("review_scores", "presentation", "DOUBLE");
        modifyColumnNullable("review_scores", "total",        "DOUBLE");
        modifyColumnNullable("review_scores", "highlight",    "VARCHAR(1000)");
        modifyColumnNullable("review_scores", "weakness",     "VARCHAR(1000)");
        modifyColumnNullable("review_scores", "submitted_at", "DATETIME(6)");
        // interview_scores
        modifyColumnNullable("interview_scores", "topic",        "DOUBLE");
        modifyColumnNullable("interview_scores", "process",      "DOUBLE");
        modifyColumnNullable("interview_scores", "operation",    "DOUBLE");
        modifyColumnNullable("interview_scores", "result",       "DOUBLE");
        modifyColumnNullable("interview_scores", "total",        "DOUBLE");
        modifyColumnNullable("interview_scores", "highlight",    "VARCHAR(1000)");
        modifyColumnNullable("interview_scores", "weakness",     "VARCHAR(1000)");
        modifyColumnNullable("interview_scores", "submitted_at", "DATETIME(6)");
    }

    private void modifyColumnNullable(String table, String column, String typeDef) {
        try {
            jdbcTemplate.execute(
                "ALTER TABLE " + table + " MODIFY COLUMN " + column + " " + typeDef + " NULL");
        } catch (Exception e) {
            // 忽略（列不存在等异常不影响启动）
        }
    }

    private void ensureReviewerInstitutionChangesTable() {
        jdbcTemplate.execute("CREATE TABLE IF NOT EXISTS reviewer_institution_changes (" +
                "id BIGINT NOT NULL AUTO_INCREMENT," +
                "reviewer_id BIGINT NOT NULL," +
                "old_institution_id BIGINT NULL," +
                "old_institution_name VARCHAR(256) NULL," +
                "new_institution_id BIGINT NULL," +
                "new_institution_name VARCHAR(256) NULL," +
                "reason VARCHAR(500) NULL," +
                "changed_by_id BIGINT NULL," +
                "changed_by_name VARCHAR(64) NULL," +
                "changed_at DATETIME(6) NOT NULL," +
                "PRIMARY KEY (id)," +
                "INDEX idx_ric_reviewer (reviewer_id)" +
                ")");
    }

    private void ensureRecuseReasonDictionary() {
        String[] codes  = {"GUIDED_PROJECT", "KNOW_LEADER", "OTHER_EXCHANGE", "OTHER"};
        String[] labels = {"参与该项目辅导工作", "与项目负责人相熟", "与该项目存在其他形式交流", "其他"};
        for (int i = 0; i < codes.length; i++) {
            jdbcTemplate.update(
                "INSERT IGNORE INTO dictionary_items (type, code, label, active, created_at) VALUES (?,?,?,1,NOW())",
                "recuse_reason", codes[i], labels[i]);
        }
    }

    private void ensureReviewerProfilesTable() {
        jdbcTemplate.execute("CREATE TABLE IF NOT EXISTS reviewer_profiles (" +
                "user_id BIGINT NOT NULL," +
                "gender VARCHAR(8) NULL," +
                "job_position VARCHAR(64) NULL," +
                "id_number VARCHAR(64) NULL," +
                "id_number_masked VARCHAR(32) NULL," +
                "id_card_front_url VARCHAR(500) NULL," +
                "id_card_back_url VARCHAR(500) NULL," +
                "bank_name VARCHAR(128) NULL," +
                "bank_card_no VARCHAR(128) NULL," +
                "bank_card_no_masked VARCHAR(32) NULL," +
                "backgrounds_json TEXT NULL," +
                "tools_json TEXT NULL," +
                "topics_json TEXT NULL," +
                "created_at DATETIME(6) NOT NULL," +
                "updated_at DATETIME(6) NOT NULL," +
                "PRIMARY KEY (user_id)," +
                "CONSTRAINT fk_reviewer_profiles_user FOREIGN KEY (user_id) REFERENCES user_accounts(id)" +
                ")");
    }
}
