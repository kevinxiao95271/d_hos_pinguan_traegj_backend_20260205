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
    }

    private void ensureColumn(String tableName, String columnName, String definition) {
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
}
