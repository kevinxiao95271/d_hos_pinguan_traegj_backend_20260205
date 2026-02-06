package com.trae.pinguan.config;

import com.zaxxer.hikari.HikariDataSource;
import java.util.HashMap;
import java.util.Map;
import javax.sql.DataSource;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
@EnableConfigurationProperties(AppDataSourceProperties.class)
public class DataSourceConfig {
    @Bean
    public DataSource ds1(AppDataSourceProperties properties) {
        return buildDataSource(properties.getDs1());
    }

    @Bean
    public DataSource ds2(AppDataSourceProperties properties) {
        return buildDataSource(properties.getDs2());
    }

    @Bean
    public DataSource ds3(AppDataSourceProperties properties) {
        return buildDataSource(properties.getDs3());
    }

    @Primary
    @Bean
    public DataSource dataSource(AppDataSourceProperties properties, DataSource ds1, DataSource ds2, DataSource ds3) {
        RoutingDataSource routingDataSource = new RoutingDataSource();
        Map<Object, Object> targets = new HashMap<>();
        targets.put("ds1", ds1);
        targets.put("ds2", ds2);
        targets.put("ds3", ds3);
        routingDataSource.setTargetDataSources(targets);
        routingDataSource.setDefaultTargetDataSource(ds1);
        DataSourceContext.setCurrent(properties.getActive() == null ? "ds1" : properties.getActive());
        return routingDataSource;
    }

    private DataSource buildDataSource(AppDataSourceProperties.DataSourceItem item) {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(item.getUrl());
        dataSource.setUsername(item.getUsername());
        dataSource.setPassword(item.getPassword());
        dataSource.setDriverClassName(item.getDriverClassName());
        return dataSource;
    }
}
