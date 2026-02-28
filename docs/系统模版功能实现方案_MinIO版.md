# 系统模版功能实现方案（MinIO 版）

## 一、MinIO 环境确认

### 已部署的 MinIO 服务
```yaml
services:
  minio:
    image: quay.io/minio/minio
    container_name: minio
    ports:
      - "58010:9000"  # API 端口
      - "58011:9001"  # 控制台端口
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: Ygcx2025
    command: server /data --console-address ":9001"
```

### MinIO 连接信息
- **Endpoint**: `http://119.167.165.27:58010` 或 `http://27.221.13.139:58010`
- **Access Key**: `minioadmin`
- **Secret Key**: `Ygcx2025`
- **控制台**: `http://119.167.165.27:58011` 或 `http://27.221.13.139:58011`

### MinIO Bucket 规划
- **报名材料**: `registration-files`（已有）
- **系统模版**: `system-templates`（新建）

---

## 二、技术方案调整

### 2.1 数据库设计（不变）

#### 表：`system_template_files`

```sql
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
```

**字段变更说明**：
- `file_path` → `minio_object_name`：存储 MinIO 中的对象路径（如 `system-templates/registration_form/uuid-xxx.docx`）

---

### 2.2 MinIO 存储结构

#### Bucket: `system-templates`
```
system-templates/
  ├── registration_form/
  │   ├── {UUID}-2026浙江省医院品管大赛报名表模板.docx
  │   └── {UUID}-2026浙江省医院品管大赛报名表模板_v2.docx (历史版本)
  └── result_report/
      └── {UUID}-成果报告相关说明.docx
```

**对象命名规则**：
- 格式：`{template_type}/{UUID}-{原始文件名}`
- 示例：`registration_form/a1b2c3d4-2026浙江省医院品管大赛报名表模板.docx`

---

## 三、代码实现清单

### 3.1 新增 Maven 依赖

**文件路径：** `pom.xml`

```xml
<!-- MinIO SDK -->
<dependency>
    <groupId>io.minio</groupId>
    <artifactId>minio</artifactId>
    <version>8.5.7</version>
</dependency>
```

---

### 3.2 MinIO 配置

#### 配置文件：`application.yml`

```yaml
minio:
  endpoint: http://119.167.165.27:58010
  access-key: minioadmin
  secret-key: Ygcx2025
  bucket:
    registration-files: registration-files
    system-templates: system-templates
```

#### 配置类：`MinioProperties.java`

**文件路径：** `src/main/java/com/trae/pinguan/config/MinioProperties.java`

```java
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
```

#### 配置类：`MinioConfig.java`

**文件路径：** `src/main/java/com/trae/pinguan/config/MinioConfig.java`

```java
package com.trae.pinguan.config;

import io.minio.MinioClient;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@RequiredArgsConstructor
public class MinioConfig {
    private final MinioProperties minioProperties;
    
    @Bean
    public MinioClient minioClient() {
        return MinioClient.builder()
            .endpoint(minioProperties.getEndpoint())
            .credentials(minioProperties.getAccessKey(), minioProperties.getSecretKey())
            .build();
    }
}
```

---

### 3.3 重构文件存储服务

#### 文件路径：`src/main/java/com/trae/pinguan/service/FileStorageService.java`

**完整重构版本**：

```java
package com.trae.pinguan.service;

import com.trae.pinguan.config.MinioProperties;
import io.minio.*;
import io.minio.errors.*;
import io.minio.http.Method;
import java.io.IOException;
import java.io.InputStream;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class FileStorageService {
    private final MinioClient minioClient;
    private final MinioProperties minioProperties;
    
    /**
     * 存储报名材料（原有方法，使用 registration-files bucket）
     */
    public String store(Long registrationId, MultipartFile file) {
        return store(String.valueOf(registrationId), file, minioProperties.getBucket().getRegistrationFiles());
    }
    
    /**
     * 存储报名材料（原有方法，使用 registration-files bucket）
     */
    public String store(String directory, MultipartFile file) {
        return store(directory, file, minioProperties.getBucket().getRegistrationFiles());
    }
    
    /**
     * 存储系统模版（新方法，使用 system-templates bucket）
     */
    public String storeSystemTemplate(String templateType, MultipartFile file) {
        String bucketName = minioProperties.getBucket().getSystemTemplates();
        ensureBucketExists(bucketName);
        
        String objectName = templateType + "/" + UUID.randomUUID() + "-" + file.getOriginalFilename();
        
        try (InputStream inputStream = file.getInputStream()) {
            minioClient.putObject(
                PutObjectArgs.builder()
                    .bucket(bucketName)
                    .object(objectName)
                    .stream(inputStream, file.getSize(), -1)
                    .contentType(file.getContentType())
                    .build()
            );
            return objectName; // 返回对象名称（路径）
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO 文件上传失败: " + ex.getMessage(), ex);
        }
    }
    
    /**
     * 通用存储方法
     */
    private String store(String directory, MultipartFile file, String bucketName) {
        ensureBucketExists(bucketName);
        
        String objectName = directory + "/" + UUID.randomUUID() + "-" + file.getOriginalFilename();
        
        try (InputStream inputStream = file.getInputStream()) {
            minioClient.putObject(
                PutObjectArgs.builder()
                    .bucket(bucketName)
                    .object(objectName)
                    .stream(inputStream, file.getSize(), -1)
                    .contentType(file.getContentType())
                    .build()
            );
            return objectName;
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO 文件上传失败: " + ex.getMessage(), ex);
        }
    }
    
    /**
     * 生成预签名下载 URL（7天有效期）
     */
    public String getPresignedUrl(String objectName, String bucketName) {
        try {
            return minioClient.getPresignedObjectUrl(
                GetPresignedObjectUrlArgs.builder()
                    .method(Method.GET)
                    .bucket(bucketName)
                    .object(objectName)
                    .expiry(7, TimeUnit.DAYS)
                    .build()
            );
        } catch (Exception ex) {
            throw new IllegalStateException("生成预签名 URL 失败: " + ex.getMessage(), ex);
        }
    }
    
    /**
     * 获取文件流（直接下载）
     */
    public InputStream getInputStream(String objectName, String bucketName) {
        try {
            return minioClient.getObject(
                GetObjectArgs.builder()
                    .bucket(bucketName)
                    .object(objectName)
                    .build()
            );
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO 文件读取失败: " + ex.getMessage(), ex);
        }
    }
    
    /**
     * 删除文件
     */
    public void delete(String objectName) {
        delete(objectName, minioProperties.getBucket().getRegistrationFiles());
    }
    
    /**
     * 删除系统模版文件
     */
    public void deleteSystemTemplate(String objectName) {
        delete(objectName, minioProperties.getBucket().getSystemTemplates());
    }
    
    /**
     * 通用删除方法
     */
    private void delete(String objectName, String bucketName) {
        try {
            if (objectName == null || objectName.trim().isEmpty()) {
                return;
            }
            minioClient.removeObject(
                RemoveObjectArgs.builder()
                    .bucket(bucketName)
                    .object(objectName)
                    .build()
            );
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO 文件删除失败: " + ex.getMessage(), ex);
        }
    }
    
    /**
     * 确保 Bucket 存在
     */
    private void ensureBucketExists(String bucketName) {
        try {
            boolean exists = minioClient.bucketExists(
                BucketExistsArgs.builder().bucket(bucketName).build()
            );
            if (!exists) {
                minioClient.makeBucket(
                    MakeBucketArgs.builder().bucket(bucketName).build()
                );
            }
        } catch (Exception ex) {
            throw new IllegalStateException("MinIO Bucket 检查/创建失败: " + ex.getMessage(), ex);
        }
    }
}
```

---

### 3.4 新建文件（与原方案相同，但使用 MinIO）

#### 1. Entity 实体类
**文件路径：** `src/main/java/com/trae/pinguan/domain/entity/SystemTemplateFile.java`

```java
package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.time.LocalDateTime;
import javax.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "system_template_files")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class SystemTemplateFile {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 64)
    private String templateType;
    
    @Column(nullable = false, length = 200)
    private String fileName;
    
    @Column(nullable = false, length = 300)
    private String minioObjectName; // MinIO 对象名称
    
    @Column(nullable = false)
    private Long fileSize;
    
    @Column(nullable = false)
    private Integer version;
    
    @Column(nullable = false)
    private Boolean isActive;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "uploaded_by")
    @JsonIgnore
    private UserAccount uploadedBy;
    
    @Column(nullable = false)
    private LocalDateTime uploadedAt;
    
    @Column(length = 500)
    private String description;
}
```

#### 2. Enum 枚举类
**文件路径：** `src/main/java/com/trae/pinguan/domain/enums/SystemTemplateType.java`

```java
package com.trae.pinguan.domain.enums;

import lombok.Getter;

@Getter
public enum SystemTemplateType {
    REGISTRATION_FORM("registration_form", "报名表模版"),
    RESULT_REPORT("result_report", "成果报告说明");
    
    private final String code;
    private final String label;
    
    SystemTemplateType(String code, String label) {
        this.code = code;
        this.label = label;
    }
    
    public static SystemTemplateType fromCode(String code) {
        for (SystemTemplateType type : values()) {
            if (type.code.equals(code)) {
                return type;
            }
        }
        throw new IllegalArgumentException("未知的模版类型: " + code);
    }
}
```

#### 3. Repository 接口
**文件路径：** `src/main/java/com/trae/pinguan/repository/SystemTemplateFileRepository.java`

```java
package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.SystemTemplateFile;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface SystemTemplateFileRepository extends JpaRepository<SystemTemplateFile, Long> {
    
    /**
     * 查询指定类型的激活模版
     */
    Optional<SystemTemplateFile> findByTemplateTypeAndIsActiveTrue(String templateType);
    
    /**
     * 查询所有激活模版
     */
    List<SystemTemplateFile> findByIsActiveTrue();
    
    /**
     * 查询指定类型的所有模版（含历史）
     */
    List<SystemTemplateFile> findByTemplateTypeOrderByVersionDesc(String templateType);
    
    /**
     * 获取指定类型的最大版本号
     */
    @Query("SELECT MAX(t.version) FROM SystemTemplateFile t WHERE t.templateType = :templateType")
    Integer findMaxVersionByType(@Param("templateType") String templateType);
    
    /**
     * 停用指定类型的所有模版
     */
    @Modifying
    @Query("UPDATE SystemTemplateFile t SET t.isActive = false WHERE t.templateType = :templateType")
    void deactivateByType(@Param("templateType") String templateType);
}
```

#### 4. Service 服务层
**文件路径：** `src/main/java/com/trae/pinguan/service/SystemTemplateFileService.java`

```java
package com.trae.pinguan.service;

import com.trae.pinguan.config.MinioProperties;
import com.trae.pinguan.domain.entity.SystemTemplateFile;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.SystemTemplateType;
import com.trae.pinguan.repository.SystemTemplateFileRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.SystemTemplateDTO;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class SystemTemplateFileService {
    private final SystemTemplateFileRepository repository;
    private final UserAccountRepository userAccountRepository;
    private final FileStorageService fileStorageService;
    private final MinioProperties minioProperties;
    
    /**
     * 上传新模版（自动版本递增，停用旧版本）
     */
    @Transactional
    public SystemTemplateDTO uploadTemplate(SystemTemplateType type, MultipartFile file, 
                                           Long uploaderId, String description) {
        // 1. 获取当前最大版本号
        Integer maxVersion = repository.findMaxVersionByType(type.getCode());
        int newVersion = (maxVersion == null) ? 1 : maxVersion + 1;
        
        // 2. 停用该类型的旧版本
        repository.deactivateByType(type.getCode());
        
        // 3. 存储文件到 MinIO
        String objectName = fileStorageService.storeSystemTemplate(type.getCode(), file);
        
        // 4. 获取上传人信息
        UserAccount uploader = null;
        if (uploaderId != null) {
            uploader = userAccountRepository.findById(uploaderId).orElse(null);
        }
        
        // 5. 创建新记录
        SystemTemplateFile template = SystemTemplateFile.builder()
            .templateType(type.getCode())
            .fileName(file.getOriginalFilename())
            .minioObjectName(objectName)
            .fileSize(file.getSize())
            .version(newVersion)
            .isActive(true)
            .uploadedBy(uploader)
            .uploadedAt(LocalDateTime.now())
            .description(description)
            .build();
        
        SystemTemplateFile saved = repository.save(template);
        return toDTO(saved);
    }
    
    /**
     * 获取指定类型的激活模版
     */
    public SystemTemplateDTO getActiveTemplate(SystemTemplateType type) {
        return repository.findByTemplateTypeAndIsActiveTrue(type.getCode())
            .map(this::toDTO)
            .orElse(null);
    }
    
    /**
     * 获取所有激活模版列表
     */
    public List<SystemTemplateDTO> getAllActiveTemplates() {
        return repository.findByIsActiveTrue().stream()
            .map(this::toDTO)
            .collect(Collectors.toList());
    }
    
    /**
     * 查看历史版本
     */
    public List<SystemTemplateDTO> listTemplateHistory(SystemTemplateType type) {
        return repository.findByTemplateTypeOrderByVersionDesc(type.getCode()).stream()
            .map(this::toDTO)
            .collect(Collectors.toList());
    }
    
    /**
     * 根据 ID 获取模版
     */
    public SystemTemplateFile getById(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("模版不存在"));
    }
    
    /**
     * 删除模版
     */
    @Transactional
    public void deleteTemplate(Long templateId) {
        SystemTemplateFile template = getById(templateId);
        
        // 删除 MinIO 文件
        fileStorageService.deleteSystemTemplate(template.getMinioObjectName());
        
        // 删除数据库记录
        repository.deleteById(templateId);
    }
    
    /**
     * 生成下载 URL
     */
    public String generateDownloadUrl(Long templateId) {
        SystemTemplateFile template = getById(templateId);
        String bucketName = minioProperties.getBucket().getSystemTemplates();
        return fileStorageService.getPresignedUrl(template.getMinioObjectName(), bucketName);
    }
    
    /**
     * 转换为 DTO
     */
    private SystemTemplateDTO toDTO(SystemTemplateFile entity) {
        return SystemTemplateDTO.builder()
            .id(entity.getId())
            .templateType(entity.getTemplateType())
            .fileName(entity.getFileName())
            .fileSize(entity.getFileSize())
            .version(entity.getVersion())
            .isActive(entity.getIsActive())
            .uploadedBy(entity.getUploadedBy() != null ? entity.getUploadedBy().getName() : null)
            .uploadedAt(entity.getUploadedAt())
            .description(entity.getDescription())
            .build();
    }
}
```

#### 5. Controller 控制器
**文件路径：** `src/main/java/com/trae/pinguan/web/SystemTemplateController.java`

```java
package com.trae.pinguan.web;

import com.trae.pinguan.config.MinioProperties;
import com.trae.pinguan.domain.entity.SystemTemplateFile;
import com.trae.pinguan.domain.enums.SystemTemplateType;
import com.trae.pinguan.service.FileStorageService;
import com.trae.pinguan.service.SystemTemplateFileService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.SystemTemplateDTO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.io.InputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/system-templates")
@RequiredArgsConstructor
@Tag(name = "系统模版")
public class SystemTemplateController {
    private final SystemTemplateFileService templateService;
    private final FileStorageService fileStorageService;
    private final MinioProperties minioProperties;
    
    /**
     * OPS 上传/更新模版
     */
    @PostMapping("/upload")
    @Operation(summary = "上传系统模版（仅 OPS）", security = @SecurityRequirement(name = "BearerAuth"))
    public ApiResponse<SystemTemplateDTO> upload(
            @RequestParam String templateType,
            @RequestParam(required = false) String description,
            @RequestPart MultipartFile file,
            HttpServletRequest request) {
        
        // 权限校验：仅 OPS
        String role = (String) request.getAttribute("role");
        if (!"OPS".equals(role)) {
            throw new AccessDeniedException("仅限系统运维人员操作");
        }
        
        // 获取上传人 ID
        String userIdStr = (String) request.getAttribute("userId");
        Long uploaderId = userIdStr != null ? Long.parseLong(userIdStr) : null;
        
        // 上传模版
        SystemTemplateType type = SystemTemplateType.fromCode(templateType);
        SystemTemplateDTO dto = templateService.uploadTemplate(type, file, uploaderId, description);
        
        return ApiResponse.ok(dto);
    }
    
    /**
     * 获取所有激活模版列表（公开）
     */
    @GetMapping("/active")
    @Operation(summary = "获取激活模版列表（公开）")
    public ApiResponse<List<SystemTemplateDTO>> listActive() {
        return ApiResponse.ok(templateService.getAllActiveTemplates());
    }
    
    /**
     * 下载模版文件（公开，返回预签名 URL 或直接流式下载）
     */
    @GetMapping("/{id}/download")
    @Operation(summary = "下载模版文件（公开）")
    public ResponseEntity<?> download(@PathVariable Long id, 
                                     @RequestParam(defaultValue = "false") boolean redirect) {
        SystemTemplateFile template = templateService.getById(id);
        
        // 方式1：返回预签名 URL（前端重定向下载）
        if (redirect) {
            String presignedUrl = templateService.generateDownloadUrl(id);
            return ResponseEntity.status(302)
                .header(HttpHeaders.LOCATION, presignedUrl)
                .build();
        }
        
        // 方式2：直接流式下载
        String bucketName = minioProperties.getBucket().getSystemTemplates();
        InputStream inputStream = fileStorageService.getInputStream(
            template.getMinioObjectName(), bucketName
        );
        
        String encodedFilename = URLEncoder.encode(template.getFileName(), StandardCharsets.UTF_8)
            .replace("+", "%20");
        
        return ResponseEntity.ok()
            .contentType(MediaType.APPLICATION_OCTET_STREAM)
            .header(HttpHeaders.CONTENT_DISPOSITION, 
                    "attachment; filename*=UTF-8''" + encodedFilename)
            .body(new InputStreamResource(inputStream));
    }
    
    /**
     * OPS 查看历史版本
     */
    @GetMapping("/history/{templateType}")
    @Operation(summary = "查看历史版本（仅 OPS）", security = @SecurityRequirement(name = "BearerAuth"))
    public ApiResponse<List<SystemTemplateDTO>> listHistory(
            @PathVariable String templateType,
            HttpServletRequest request) {
        
        // 权限校验：仅 OPS
        String role = (String) request.getAttribute("role");
        if (!"OPS".equals(role)) {
            throw new AccessDeniedException("仅限系统运维人员操作");
        }
        
        SystemTemplateType type = SystemTemplateType.fromCode(templateType);
        return ApiResponse.ok(templateService.listTemplateHistory(type));
    }
    
    /**
     * OPS 删除模版
     */
    @DeleteMapping("/{id}")
    @Operation(summary = "删除模版（仅 OPS）", security = @SecurityRequirement(name = "BearerAuth"))
    public ApiResponse<Void> delete(@PathVariable Long id, HttpServletRequest request) {
        
        // 权限校验：仅 OPS
        String role = (String) request.getAttribute("role");
        if (!"OPS".equals(role)) {
            throw new AccessDeniedException("仅限系统运维人员操作");
        }
        
        templateService.deleteTemplate(id);
        return ApiResponse.ok(null);
    }
}
```

#### 6. DTO 数据传输对象
**文件路径：** `src/main/java/com/trae/pinguan/web/dto/SystemTemplateDTO.java`

```java
package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "系统模版信息")
public class SystemTemplateDTO {
    @Schema(description = "模版ID")
    private Long id;
    
    @Schema(description = "模版类型", example = "registration_form")
    private String templateType;
    
    @Schema(description = "文件名")
    private String fileName;
    
    @Schema(description = "文件大小（字节）")
    private Long fileSize;
    
    @Schema(description = "版本号")
    private Integer version;
    
    @Schema(description = "是否激活")
    private Boolean isActive;
    
    @Schema(description = "上传人")
    private String uploadedBy;
    
    @Schema(description = "上传时间")
    private LocalDateTime uploadedAt;
    
    @Schema(description = "描述")
    private String description;
}
```

---

### 3.5 修改文件

#### 1. JWT 权限过滤器（不变）
**文件路径：** `src/main/java/com/trae/pinguan/config/JwtAuthorizationFilter.java`

在 `doFilterInternal` 方法的白名单中添加（约第 54 行之后）：

```java
// 5. 系统模版下载接口（公开）
if ("GET".equalsIgnoreCase(method) && 
    (path.equals("/api/system-templates/active") || 
     path.matches("^/api/system-templates/\\d+/download$"))) {
    filterChain.doFilter(request, response);
    return;
}
```

---

### 3.6 数据库建表脚本

**文件路径：** `scripts/create_system_template_table.sql`

```sql
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
```

---

### 3.7 初始化脚本

**文件路径：** `scripts/init_system_templates_minio.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化系统模版到 MinIO
将根目录的两个 .docx 文件上传到 MinIO 并在数据库中创建记录
"""

import pymysql
from pathlib import Path
from minio import Minio
from minio.error import S3Error
import uuid

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# MinIO 配置
MINIO_CONFIG = {
    'endpoint': '119.167.165.27:58010',
    'access_key': 'minioadmin',
    'secret_key': 'Ygcx2025',
    'secure': False  # HTTP
}

BUCKET_NAME = 'system-templates'

# 模版文件配置
TEMPLATE_FILES = [
    {
        'source': '2026浙江省医院品管大赛报名表模板.docx',
        'type': 'registration_form'
    },
    {
        'source': '成果报告相关说明.docx',
        'type': 'result_report'
    }
]

def init_minio_client():
    """初始化 MinIO 客户端"""
    return Minio(
        MINIO_CONFIG['endpoint'],
        access_key=MINIO_CONFIG['access_key'],
        secret_key=MINIO_CONFIG['secret_key'],
        secure=MINIO_CONFIG['secure']
    )

def ensure_bucket_exists(client):
    """确保 bucket 存在"""
    try:
        if not client.bucket_exists(BUCKET_NAME):
            client.make_bucket(BUCKET_NAME)
            print(f"Created bucket: {BUCKET_NAME}")
        else:
            print(f"Bucket already exists: {BUCKET_NAME}")
    except S3Error as e:
        print(f"Error ensuring bucket: {e}")
        raise

def upload_to_minio(client, file_path, object_name):
    """上传文件到 MinIO"""
    try:
        client.fput_object(
            BUCKET_NAME,
            object_name,
            str(file_path),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        print(f"Uploaded: {object_name}")
        return True
    except S3Error as e:
        print(f"Error uploading {object_name}: {e}")
        return False

def insert_db_record(conn, template_info):
    """插入数据库记录"""
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO system_template_files 
        (template_type, file_name, minio_object_name, file_size, version, is_active, uploaded_at)
        VALUES (%s, %s, %s, %s, 1, TRUE, NOW())
        """
        cursor.execute(sql, (
            template_info['type'],
            template_info['file_name'],
            template_info['object_name'],
            template_info['file_size']
        ))
        conn.commit()
        print(f"DB record created for: {template_info['file_name']}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error inserting DB record: {e}")
        return False
    finally:
        cursor.close()

def main():
    print("=" * 60)
    print("系统模版初始化脚本（MinIO 版）")
    print("=" * 60)
    
    # 1. 初始化 MinIO 客户端
    print("\n[1/4] 初始化 MinIO 客户端...")
    minio_client = init_minio_client()
    
    # 2. 确保 bucket 存在
    print("\n[2/4] 确保 Bucket 存在...")
    ensure_bucket_exists(minio_client)
    
    # 3. 连接数据库
    print("\n[3/4] 连接数据库...")
    conn = pymysql.connect(**DB_CONFIG)
    print("Database connected")
    
    # 4. 处理每个模版文件
    print("\n[4/4] 处理模版文件...")
    success_count = 0
    
    for file_info in TEMPLATE_FILES:
        print(f"\n处理: {file_info['source']}")
        
        # 检查源文件是否存在
        source_path = Path(file_info['source'])
        if not source_path.exists():
            print(f"  警告: 源文件不存在，跳过")
            continue
        
        # 生成 MinIO 对象名称
        object_name = f"{file_info['type']}/{uuid.uuid4()}-{source_path.name}"
        
        # 上传到 MinIO
        if upload_to_minio(minio_client, source_path, object_name):
            # 插入数据库记录
            template_info = {
                'type': file_info['type'],
                'file_name': source_path.name,
                'object_name': object_name,
                'file_size': source_path.stat().st_size
            }
            
            if insert_db_record(conn, template_info):
                success_count += 1
                print(f"  成功: {source_path.name} -> {object_name}")
    
    # 5. 清理
    conn.close()
    
    # 6. 总结
    print("\n" + "=" * 60)
    print(f"初始化完成！成功处理 {success_count}/{len(TEMPLATE_FILES)} 个模版文件")
    print("=" * 60)
    
    # 7. 验证
    print("\n验证结果:")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT id, template_type, file_name, version, is_active FROM system_template_files")
    rows = cursor.fetchall()
    
    if rows:
        print(f"\n数据库中的模版记录（共 {len(rows)} 条）:")
        for row in rows:
            print(f"  ID={row[0]}, Type={row[1]}, File={row[2]}, Version={row[3]}, Active={row[4]}")
    else:
        print("  数据库中没有模版记录")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
```

**依赖安装**：
```bash
pip install pymysql minio
```

---

## 四、实施步骤

### Step 1: 添加 Maven 依赖
```bash
# 编辑 pom.xml，添加 MinIO SDK 依赖
# 运行 mvn clean install 下载依赖
```

### Step 2: 配置 MinIO
```bash
# 编辑 application.yml，添加 MinIO 配置
# 创建 MinioProperties.java 和 MinioConfig.java
```

### Step 3: 重构 FileStorageService
```bash
# 完全重写 FileStorageService.java，使用 MinIO API
```

### Step 4: 创建数据库表
```bash
# 在远程 MySQL 数据库执行 create_system_template_table.sql
```

### Step 5: 创建系统模版相关代码
```bash
# 依次创建：
# - SystemTemplateFile.java (Entity)
# - SystemTemplateType.java (Enum)
# - SystemTemplateFileRepository.java (Repository)
# - SystemTemplateFileService.java (Service)
# - SystemTemplateController.java (Controller)
# - SystemTemplateDTO.java (DTO)
```

### Step 6: 修改 JWT 过滤器
```bash
# 在 JwtAuthorizationFilter.java 添加白名单
```

### Step 7: 初始化数据
```bash
# 运行 init_system_templates_minio.py 脚本
# 将两个 .docx 文件上传到 MinIO 并创建数据库记录
```

### Step 8: 编译部署
```bash
mvn clean package
# 部署 target/pinguan-backend-0.0.1-SNAPSHOT.jar
```

### Step 9: 测试验证
```bash
# 测试 MinIO Bucket 是否创建成功
# 测试 API 端点是否正常工作
```

---

## 五、测试验证

### 5.1 MinIO 验证
```bash
# 访问 MinIO 控制台
http://119.167.165.27:58011

# 登录信息
Username: minioadmin
Password: Ygcx2025

# 检查 system-templates bucket 是否存在
# 检查是否有 registration_form/ 和 result_report/ 目录
```

### 5.2 API 测试

#### 1. 获取激活模版列表（公开）
```bash
curl -X GET http://localhost:6031/api/system-templates/active
```

**预期响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "templateType": "registration_form",
      "fileName": "2026浙江省医院品管大赛报名表模板.docx",
      "fileSize": 17671,
      "version": 1,
      "isActive": true,
      "uploadedBy": null,
      "uploadedAt": "2026-02-27T15:30:00",
      "description": null
    },
    {
      "id": 2,
      "templateType": "result_report",
      "fileName": "成果报告相关说明.docx",
      "fileSize": 16967,
      "version": 1,
      "isActive": true,
      "uploadedBy": null,
      "uploadedAt": "2026-02-27T15:30:00",
      "description": null
    }
  ]
}
```

#### 2. 下载模版文件（直接下载）
```bash
curl -X GET http://localhost:6031/api/system-templates/1/download \
  -o downloaded_template.docx
```

#### 3. 下载模版文件（预签名 URL）
```bash
curl -X GET "http://localhost:6031/api/system-templates/1/download?redirect=true"
```

#### 4. OPS 上传新模版
```bash
curl -X POST http://localhost:6031/api/system-templates/upload \
  -H "Authorization: Bearer {OPS_TOKEN}" \
  -F "templateType=registration_form" \
  -F "description=2026年第2版" \
  -F "file=@new_template.docx"
```

---

## 六、修改工作量统计（MinIO 版）

| 类型 | 数量 | 预估行数 | 说明 |
|------|------|---------|------|
| **新增文件** | | | |
| Entity | 1 | 60 | SystemTemplateFile.java |
| Enum | 1 | 30 | SystemTemplateType.java |
| Repository | 1 | 40 | SystemTemplateFileRepository.java |
| Service | 1 | 180 | SystemTemplateFileService.java |
| Controller | 1 | 120 | SystemTemplateController.java |
| DTO | 1 | 50 | SystemTemplateDTO.java |
| Config | 2 | 60 | MinioProperties.java + MinioConfig.java |
| SQL 脚本 | 1 | 20 | create_system_template_table.sql |
| Python 脚本 | 1 | 150 | init_system_templates_minio.py |
| **修改文件** | | | |
| Service 重构 | 1 | +150 | FileStorageService.java（完全重写为 MinIO 版本） |
| Filter 修改 | 1 | +10 | JwtAuthorizationFilter.java |
| pom.xml | 1 | +8 | 添加 MinIO 依赖 |
| application.yml | 1 | +8 | 添加 MinIO 配置 |
| **合计** | **14** | **886** | |

### 实施时间估算（MinIO 版）
1. 添加 Maven 依赖：5 分钟
2. 配置 MinIO（Config + yml）：15 分钟
3. 重构 FileStorageService：40 分钟
4. 数据库建表：10 分钟
5. 编写实体类和枚举：20 分钟
6. 编写 Repository 和 Service：50 分钟
7. 编写 Controller 和 DTO：40 分钟
8. 修改 JwtAuthorizationFilter：10 分钟
9. 编写初始化脚本：30 分钟
10. 测试和调试：40 分钟
11. 部署和验证：20 分钟

**总计：约 4.5 小时**（比本地文件系统版本多 1.5 小时）

---

## 七、优势对比

### MinIO 版 vs 本地文件系统版

| 特性 | MinIO 版 | 本地文件系统版 |
|------|---------|---------------|
| **扩展性** | ✅ 支持分布式存储 | ❌ 单机受限 |
| **高可用** | ✅ 支持多副本 | ❌ 单点故障 |
| **访问速度** | ✅ CDN 加速（可选） | ⚠️ 受网络带宽限制 |
| **存储成本** | ✅ 对象存储成本低 | ⚠️ 磁盘空间有限 |
| **管理便利** | ✅ 可视化控制台 | ❌ 需手动管理文件 |
| **迁移成本** | ✅ 统一存储架构 | ⚠️ 后续迁移复杂 |
| **开发复杂度** | ⚠️ 需要集成 SDK | ✅ 原生 Java API |

---

## 八、总结

### 核心改动
1. **引入 MinIO SDK**：使用官方 Java SDK 操作对象存储
2. **重构 FileStorageService**：完全基于 MinIO API 重写
3. **配置管理**：通过 `application.yml` 集中管理 MinIO 连接信息
4. **存储路径变更**：数据库字段从 `file_path` 改为 `minio_object_name`
5. **下载方式优化**：支持预签名 URL 和直接流式下载两种方式

### 技术亮点
- **统一存储架构**：报名材料和系统模版都使用 MinIO
- **版本管理机制**：与原方案一致（版本递增、激活控制）
- **权限分级设计**：OPS 管理、用户公开下载
- **扩展性强**：支持未来添加更多 Bucket 和文件类型

---

**文档版本：** v2.0 (MinIO 版)  
**编写日期：** 2026-02-27  
**编写人：** AI Assistant
