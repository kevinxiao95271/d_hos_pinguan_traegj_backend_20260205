package com.trae.pinguan.web;

import com.trae.pinguan.config.MinioProperties;
import com.trae.pinguan.domain.entity.MaterialFile;
import com.trae.pinguan.repository.ReviewTaskRepository;
import com.trae.pinguan.service.FileStorageService;
import com.trae.pinguan.service.MaterialService;
import com.trae.pinguan.web.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import javax.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/materials")
@RequiredArgsConstructor
@Tag(name = "报名材料")
@SecurityRequirement(name = "BearerAuth")
public class MaterialController {
    private final MaterialService materialService;
    private final FileStorageService fileStorageService;
    private final MinioProperties minioProperties;
    private final ReviewTaskRepository reviewTaskRepository;

    @DeleteMapping("/{id}")
    @Operation(summary = "删除材料")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        materialService.delete(id);
        return ApiResponse.ok(null);
    }
    
    @GetMapping("/{id}/download")
    @Operation(summary = "下载材料文件")
    public ResponseEntity<InputStreamResource> download(@PathVariable Long id, HttpServletRequest request) {
        MaterialFile material = materialService.getById(id);
        
        // 权限检查
        checkDownloadPermission(material, request);
        
        // 从 MinIO 获取文件流
        String bucketName = minioProperties.getBucket().getRegistrationFiles();
        InputStream inputStream = fileStorageService.getInputStream(
            material.getFileUrl(), bucketName
        );
        
        // URL 编码文件名（支持中文）
        String encodedFilename;
        try {
            encodedFilename = URLEncoder.encode(material.getFileName(), "UTF-8")
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
     * 检查材料下载权限
     */
    private void checkDownloadPermission(MaterialFile material, HttpServletRequest request) {
        String role = (String) request.getAttribute("role");
        Long userId = Long.parseLong((String) request.getAttribute("userId"));
        
        // OPS、COMMITTEE、COMMITTEE_ADMIN 可以下载所有材料
        if ("OPS".equals(role) || "COMMITTEE".equals(role) || "COMMITTEE_ADMIN".equals(role)) {
            return;
        }
        
        // CONTESTANT（参赛者）只能下载自己申请的报名材料
        if ("CONTESTANT".equals(role)) {
            Long applicantId = material.getRegistration().getApplicant().getId();
            if (!userId.equals(applicantId)) {
                throw new ResponseStatusException(HttpStatus.FORBIDDEN, "无权下载该材料，您只能下载自己提交的报名材料");
            }
            return;
        }
        
        // REVIEWER（评委）只能下载分配给自己的评审任务的材料
        if ("REVIEWER".equals(role)) {
            Long registrationId = material.getRegistration().getId();
            boolean hasReviewTask = reviewTaskRepository.existsByReviewerIdAndRegistrationId(userId, registrationId);
            if (!hasReviewTask) {
                throw new ResponseStatusException(HttpStatus.FORBIDDEN, "无权下载该材料，您只能下载分配给您评审的项目材料");
            }
            return;
        }
        
        // 其他未知角色，拒绝访问
        throw new ResponseStatusException(HttpStatus.FORBIDDEN, "无权下载材料");
    }
}
