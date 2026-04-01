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
        ensureReviewerProfilesTable();
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
