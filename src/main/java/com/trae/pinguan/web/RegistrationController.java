package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.ActivityInfo;
import com.trae.pinguan.domain.entity.MaterialFile;
import com.trae.pinguan.domain.entity.ProjectSummary;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.RegistrationMember;
import com.trae.pinguan.service.MaterialService;
import com.trae.pinguan.service.RegistrationService;
import com.trae.pinguan.service.ReviewService;
import com.trae.pinguan.web.dto.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/registrations")
@RequiredArgsConstructor
@Tag(name = "报名")
@SecurityRequirement(name = "BearerAuth")
public class RegistrationController {
    private final RegistrationService registrationService;
    private final MaterialService materialService;
    private final ReviewService reviewService;
    private final javax.servlet.http.HttpServletRequest request;

    @PostMapping
    @Operation(summary = "创建报名")
    public ApiResponse<Registration> create(@Valid @RequestBody RegistrationCreateRequest request) {
        // 自动从token获取当前用户ID作为申请人
        Long applicantId = getCurrentUserId();
        request.setApplicantId(applicantId);
        return ApiResponse.ok(registrationService.create(request));
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新报名基本信息")
    public ApiResponse<Registration> update(@PathVariable Long id, @Valid @RequestBody RegistrationUpdateRequest request) {
        return ApiResponse.ok(registrationService.update(id, request));
    }

    @PutMapping("/{id}/members")
    @Operation(summary = "提交成员信息")
    public ApiResponse<List<RegistrationMember>> upsertMembers(@PathVariable Long id, @Valid @RequestBody MemberUpsertRequest request) {
        request.setRegistrationId(id);
        return ApiResponse.ok(registrationService.upsertMembers(request));
    }

    @PutMapping("/{id}/activity")
    @Operation(summary = "提交活动说明")
    public ApiResponse<ActivityInfo> saveActivity(@PathVariable Long id, @Valid @RequestBody ActivityInfoRequest request) {
        request.setRegistrationId(id);
        return ApiResponse.ok(registrationService.saveActivity(request));
    }

    @PutMapping("/{id}/summary")
    @Operation(summary = "提交摘要")
    public ApiResponse<ProjectSummary> saveSummary(@PathVariable Long id, @Valid @RequestBody ProjectSummaryRequest request) {
        request.setRegistrationId(id);
        return ApiResponse.ok(registrationService.saveSummary(request));
    }

    @PostMapping("/{id}/submit")
    @Operation(summary = "提交报名")
    public ApiResponse<Registration> submit(@PathVariable Long id) {
        return ApiResponse.ok(registrationService.submit(id));
    }

    @PostMapping("/{id}/return")
    @Operation(summary = "退回报名")
    public ApiResponse<Registration> returnForEdit(@PathVariable Long id) {
        return ApiResponse.ok(registrationService.returnForEdit(id));
    }

    @PostMapping("/{id}/approve")
    @Operation(summary = "通过报名")
    public ApiResponse<Registration> approve(@PathVariable Long id) {
        return ApiResponse.ok(registrationService.approve(id));
    }

    @GetMapping("/{id}")
    @Operation(summary = "报名详情")
    public ApiResponse<RegistrationDetailResponse> detail(@PathVariable Long id) {
        return ApiResponse.ok(registrationService.getDetail(id));
    }

    @GetMapping("/{id}/review-results")
    @Operation(summary = "报名评审结果")
    public ApiResponse<List<ReviewResultItem>> reviewResults(@PathVariable Long id) {
        return ApiResponse.ok(reviewService.resultsByRegistration(id));
    }

    @GetMapping("/{id}/review-details")
    @Operation(summary = "报名评审详情")
    public ApiResponse<List<ReviewStageScoreSummary>> reviewDetails(@PathVariable Long id) {
        return ApiResponse.ok(reviewService.scoreSummaryByRegistration(id));
    }

    @GetMapping
    @Operation(summary = "按赛事查询报名列表")
    public ApiResponse<List<Registration>> list(@RequestParam Long competitionId) {
        return ApiResponse.ok(registrationService.listByCompetition(competitionId));
    }

    @GetMapping("/status")
    @Operation(summary = "按赛事与状态查询报名")
    public ApiResponse<List<Registration>> listByStatus(@RequestParam Long competitionId,
                                                        @RequestParam com.trae.pinguan.domain.enums.RegistrationStatus status) {
        return ApiResponse.ok(registrationService.listByCompetitionAndStatus(competitionId, status));
    }

    @GetMapping("/my")
    @Operation(summary = "我的报名列表（参赛者端）")
    public ApiResponse<List<MyRegistrationItem>> myRegistrations() {
        // 从token中获取当前登录用户ID
        Long applicantId = getCurrentUserId();
        return ApiResponse.ok(registrationService.listMyRegistrations(applicantId));
    }

    @GetMapping("/by-applicant")
    @Operation(summary = "按报名人查询报名（需要applicantId参数）")
    public ApiResponse<List<Registration>> listByApplicant(@RequestParam Long applicantId) {
        return ApiResponse.ok(registrationService.listByApplicant(applicantId));
    }
    
    private Long getCurrentUserId() {
        Object userId = request.getAttribute("userId");
        if (userId == null) {
            throw new RuntimeException("未登录");
        }
        return Long.parseLong(userId.toString());
    }

    @GetMapping("/by-institution")
    @Operation(summary = "按机构查询报名")
    public ApiResponse<List<Registration>> listByInstitution(@RequestParam Long institutionId) {
        return ApiResponse.ok(registrationService.listByInstitution(institutionId));
    }

    @GetMapping("/institution-quota")
    @Operation(summary = "查询机构报名配额信息")
    public ApiResponse<InstitutionQuotaResponse> getInstitutionQuota(
            @RequestParam Long competitionId,
            @RequestParam Long institutionId) {
        return ApiResponse.ok(registrationService.getInstitutionQuota(competitionId, institutionId));
    }

    @PostMapping("/{id}/materials")
    @Operation(summary = "上传报名材料")
    public ApiResponse<MaterialFile> upload(@PathVariable Long id,
                                            @RequestParam String type,
                                            @RequestPart MultipartFile file) {
        return ApiResponse.ok(materialService.upload(id, type, file));
    }

    @GetMapping("/{id}/materials")
    @Operation(summary = "报名材料列表")
    public ApiResponse<List<MaterialFile>> listMaterials(@PathVariable Long id) {
        return ApiResponse.ok(materialService.list(id));
    }
}
