package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.RegistrationDraft;
import com.trae.pinguan.domain.entity.RegistrationDraftActivityInfo;
import com.trae.pinguan.domain.entity.RegistrationDraftMaterialFile;
import com.trae.pinguan.domain.entity.RegistrationDraftMember;
import com.trae.pinguan.domain.entity.RegistrationDraftProjectSummary;
import com.trae.pinguan.service.DraftMaterialService;
import com.trae.pinguan.service.RegistrationDraftService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.ActivityInfoRequest;
import com.trae.pinguan.web.dto.MemberUpsertRequest;
import com.trae.pinguan.web.dto.ProjectSummaryRequest;
import com.trae.pinguan.web.dto.RegistrationCreateRequest;
import com.trae.pinguan.web.dto.RegistrationDraftDetailResponse;
import com.trae.pinguan.web.dto.RegistrationUpdateRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import java.util.Map;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/registration-drafts")
@RequiredArgsConstructor
@Tag(name = "报名草稿")
@SecurityRequirement(name = "BearerAuth")
public class RegistrationDraftController {
    private final RegistrationDraftService draftService;
    private final DraftMaterialService draftMaterialService;
    private final HttpServletRequest request;

    @PostMapping
    @Operation(summary = "创建报名草稿")
    public ApiResponse<RegistrationDraft> create(@Valid @RequestBody RegistrationCreateRequest body) {
        body.setApplicantId(getCurrentUserId());
        return ApiResponse.ok(draftService.create(body));
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新草稿基本信息")
    public ApiResponse<RegistrationDraft> update(@PathVariable Long id,
                                                 @Valid @RequestBody RegistrationUpdateRequest body) {
        return ApiResponse.ok(draftService.update(id, getCurrentUserId(), body));
    }

    @PutMapping("/{id}/members")
    @Operation(summary = "保存草稿成员")
    public ApiResponse<List<RegistrationDraftMember>> upsertMembers(
            @PathVariable Long id, @Valid @RequestBody MemberUpsertRequest body) {
        return ApiResponse.ok(draftService.upsertMembers(id, getCurrentUserId(), body));
    }

    @PutMapping("/{id}/activity")
    @Operation(summary = "保存草稿活动说明")
    public ApiResponse<RegistrationDraftActivityInfo> saveActivity(
            @PathVariable Long id, @Valid @RequestBody ActivityInfoRequest body) {
        return ApiResponse.ok(draftService.saveActivity(id, getCurrentUserId(), body));
    }

    @PutMapping("/{id}/summary")
    @Operation(summary = "保存草稿摘要")
    public ApiResponse<RegistrationDraftProjectSummary> saveSummary(
            @PathVariable Long id, @Valid @RequestBody ProjectSummaryRequest body) {
        return ApiResponse.ok(draftService.saveSummary(id, getCurrentUserId(), body));
    }

    @PostMapping("/{id}/submit")
    @Operation(summary = "提交草稿（COPY 到正式报名，正式 id 即项目编号）")
    public ApiResponse<Registration> submit(@PathVariable Long id) {
        return ApiResponse.ok(draftService.submit(id, getCurrentUserId()));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除草稿")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        draftService.deleteDraft(id, getCurrentUserId());
        return ApiResponse.ok(null);
    }

    @GetMapping("/{id}")
    @Operation(summary = "草稿详情")
    public ApiResponse<RegistrationDraftDetailResponse> detail(@PathVariable Long id) {
        return ApiResponse.ok(draftService.getDetail(id, getCurrentUserId()));
    }

    @GetMapping("/check-duplicate")
    @Operation(summary = "同机构相似项目检测（含其他草稿）")
    public ApiResponse<List<Map<String, Object>>> checkDuplicate(
            @RequestParam Long competitionId,
            @RequestParam Long institutionId,
            @RequestParam String projectName,
            @RequestParam(required = false) Long selfDraftId) {
        return ApiResponse.ok(draftService.checkDuplicate(
                competitionId, institutionId, projectName, selfDraftId));
    }

    @PostMapping("/{id}/materials")
    @Operation(summary = "上传草稿材料")
    public ApiResponse<RegistrationDraftMaterialFile> upload(
            @PathVariable Long id,
            @RequestParam String type,
            @RequestPart MultipartFile file) {
        draftService.verifyOwnership(id, getCurrentUserId());
        return ApiResponse.ok(draftMaterialService.upload(id, type, file));
    }

    @GetMapping("/{id}/materials")
    @Operation(summary = "草稿材料列表")
    public ApiResponse<List<RegistrationDraftMaterialFile>> listMaterials(@PathVariable Long id) {
        draftService.verifyOwnership(id, getCurrentUserId());
        return ApiResponse.ok(draftMaterialService.list(id));
    }

    @DeleteMapping("/{draftId}/materials/{materialId}")
    @Operation(summary = "删除草稿材料")
    public ApiResponse<Void> deleteMaterial(@PathVariable Long draftId, @PathVariable Long materialId) {
        draftService.verifyOwnership(draftId, getCurrentUserId());
        RegistrationDraftMaterialFile material = draftMaterialService.getById(materialId);
        if (material.getDraftId() == null || !material.getDraftId().equals(draftId)) {
            throw new IllegalArgumentException("材料不属于该草稿");
        }
        draftMaterialService.delete(materialId);
        return ApiResponse.ok(null);
    }

    private Long getCurrentUserId() {
        Object userId = request.getAttribute("userId");
        if (userId == null) {
            throw new RuntimeException("未登录");
        }
        return Long.parseLong(userId.toString());
    }
}
