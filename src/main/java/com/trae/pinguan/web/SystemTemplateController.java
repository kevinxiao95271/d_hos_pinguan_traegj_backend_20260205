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
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
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
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "仅限系统运维人员操作");
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
     * 下载模版文件（公开，后端流式代理，URL永久有效）
     */
    @GetMapping("/{id}/download")
    @Operation(summary = "下载模版文件（公开）")
    public ResponseEntity<InputStreamResource> download(@PathVariable Long id) {
        SystemTemplateFile template = templateService.getById(id);
        
        // 从 MinIO 获取文件流
        String bucketName = minioProperties.getBucket().getSystemTemplates();
        InputStream inputStream = fileStorageService.getInputStream(
            template.getMinioObjectName(), bucketName
        );
        
        // URL 编码文件名（支持中文）
        String encodedFilename;
        try {
            encodedFilename = URLEncoder.encode(template.getFileName(), "UTF-8")
                .replace("+", "%20");
        } catch (UnsupportedEncodingException e) {
            throw new IllegalStateException("UTF-8 encoding not supported", e);
        }
        
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
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "仅限系统运维人员操作");
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
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "仅限系统运维人员操作");
        }
        
        templateService.deleteTemplate(id);
        return ApiResponse.ok(null);
    }
}
