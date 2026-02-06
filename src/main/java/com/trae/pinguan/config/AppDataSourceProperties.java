package com.trae.pinguan.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;

@Data
@ConfigurationProperties(prefix = "app.datasource")
public class AppDataSourceProperties {
    private String active;
    private DataSourceItem ds1;
    private DataSourceItem ds2;
    private DataSourceItem ds3;

    @Data
    public static class DataSourceItem {
        private String url;
        private String username;
        private String password;
        private String driverClassName;
    }
}
