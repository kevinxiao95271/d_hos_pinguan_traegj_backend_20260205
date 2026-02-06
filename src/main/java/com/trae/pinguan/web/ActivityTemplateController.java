package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.ActivityTemplate;
import com.trae.pinguan.service.ActivityTemplateService;
import com.trae.pinguan.web.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.nio.file.Paths;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/activity-templates")
@RequiredArgsConstructor
@Tag(name = "活动模板")
@SecurityRequirement(name = "BearerAuth")
public class ActivityTemplateController {
    private final ActivityTemplateService activityTemplateService;

    @PostMapping
    @Operation(summary = "上传活动模板")
    public ApiResponse<ActivityTemplate> upload(@RequestParam String type,
                                                @RequestPart MultipartFile file) {
        return ApiResponse.ok(activityTemplateService.upload(type, file));
    }

    @GetMapping
    @Operation(summary = "活动模板列表")
    public ApiResponse<List<ActivityTemplate>> list(@RequestParam(required = false) String type) {
        return ApiResponse.ok(activityTemplateService.list(type));
    }

    @GetMapping("/{id}/download")
    @Operation(summary = "下载活动模板")
    public ResponseEntity<Resource> download(@PathVariable Long id) {
        ActivityTemplate template = activityTemplateService.get(id);
        Resource resource = new FileSystemResource(Paths.get(template.getFileUrl()));
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + template.getFileName() + "\"")
                .body(resource);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除活动模板")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        activityTemplateService.delete(id);
        return ApiResponse.ok(null);
    }
}
