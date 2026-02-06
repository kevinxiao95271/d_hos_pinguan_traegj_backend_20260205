package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.CompetitionTemplate;
import com.trae.pinguan.service.TemplateService;
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
@RequestMapping("/api/competitions")
@RequiredArgsConstructor
@Tag(name = "赛事模板")
@SecurityRequirement(name = "BearerAuth")
public class TemplateController {
    private final TemplateService templateService;

    @PostMapping("/{id}/templates")
    @Operation(summary = "上传赛事模板")
    public ApiResponse<CompetitionTemplate> upload(@PathVariable Long id,
                                                   @RequestParam String type,
                                                   @RequestPart MultipartFile file) {
        return ApiResponse.ok(templateService.upload(id, type, file));
    }

    @GetMapping("/{id}/templates")
    @Operation(summary = "查询赛事模板列表")
    public ApiResponse<List<CompetitionTemplate>> list(@PathVariable Long id) {
        return ApiResponse.ok(templateService.list(id));
    }

    @GetMapping("/{id}/templates/{templateId}/download")
    @Operation(summary = "下载赛事模板")
    public ResponseEntity<Resource> download(@PathVariable Long id, @PathVariable Long templateId) {
        CompetitionTemplate template = templateService.get(id, templateId);
        Resource resource = new FileSystemResource(Paths.get(template.getFileUrl()));
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + template.getFileName() + "\"")
                .body(resource);
    }

    @DeleteMapping("/{id}/templates/{templateId}")
    @Operation(summary = "删除赛事模板")
    public ApiResponse<Void> delete(@PathVariable Long id, @PathVariable Long templateId) {
        templateService.delete(id, templateId);
        return ApiResponse.ok(null);
    }
}
