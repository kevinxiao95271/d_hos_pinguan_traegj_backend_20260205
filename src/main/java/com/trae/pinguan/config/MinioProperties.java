package com.trae.pinguan.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "minio")
public class MinioProperties {
    private String endpoint;
    private String accessKey;
    private String secretKey;
    private BucketConfig bucket;
    
    @Data
    public static class BucketConfig {
        private String registrationFiles;
        private String systemTemplates;
    }
}
