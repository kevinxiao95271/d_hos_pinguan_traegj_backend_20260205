package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.ActivityInfo;
import com.trae.pinguan.domain.entity.MaterialFile;
import com.trae.pinguan.domain.entity.ProjectSummary;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.RegistrationDraft;
import com.trae.pinguan.domain.entity.RegistrationDraftActivityInfo;
import com.trae.pinguan.domain.entity.RegistrationDraftMaterialFile;
import com.trae.pinguan.domain.entity.RegistrationDraftMember;
import com.trae.pinguan.domain.entity.RegistrationDraftProjectSummary;
import com.trae.pinguan.domain.entity.RegistrationMember;
import com.trae.pinguan.service.DraftMaterialService;
import com.trae.pinguan.service.RegistrationDraftCompatService;
import com.trae.pinguan.service.RegistrationDraftService;
import com.trae.pinguan.service.RegistrationService;
import com.trae.pinguan.service.MaterialService;
import com.trae.pinguan.service.ReviewService;
import com.trae.pinguan.web.dto.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.ArrayList;
import java.util.Comparator;
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
    private final RegistrationDraftService registrationDraftService;
    private final RegistrationDraftCompatService registrationDraftCompatService;
    private final MaterialService materialService;
    private final DraftMaterialService draftMaterialService;
    private final ReviewService reviewService;
    private final javax.servlet.http.HttpServletRequest request;

    @PostMapping
    @Operation(
        summary = "创建报名",
        description = "创建草稿；返回 Registration 形态且 status=DRAFT（id 为 draftId）。"
                + "兼容旧前端，亦可改用 POST /api/registration-drafts。"
    )
    public ApiResponse<Registration> create(@Valid @RequestBody RegistrationCreateRequest request) {
        Long applicantId = getCurrentUserId();
        request.setApplicantId(applicantId);
        RegistrationDraft draft = registrationDraftService.create(request);
        return ApiResponse.ok(registrationDraftCompatService.asRegistrationView(draft));
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新报名基本信息")
    public ApiResponse<Registration> update(@PathVariable Long id, @Valid @RequestBody RegistrationUpdateRequest request) {
        Long applicantId = getCurrentUserId();
        if (isDraftRoute(id, applicantId)) {
            RegistrationDraft draft = registrationDraftService.update(id, applicantId, request);
            return ApiResponse.ok(registrationDraftCompatService.asRegistrationView(draft));
        }
        return ApiResponse.ok(registrationService.update(id, request));
    }

    @PutMapping("/{id}/members")
    @Operation(summary = "提交成员信息")
    public ApiResponse<List<RegistrationMember>> upsertMembers(@PathVariable Long id, @Valid @RequestBody MemberUpsertRequest request) {
        Long applicantId = getCurrentUserId();
        if (isDraftRoute(id, applicantId)) {
            List<RegistrationDraftMember> members = registrationDraftService.upsertMembers(id, applicantId, request);
            return ApiResponse.ok(registrationDraftCompatService.mapMembers(members, id));
        }
        request.setRegistrationId(id);
        return ApiResponse.ok(registrationService.upsertMembers(request));
    }

    @PutMapping("/{id}/activity")
    @Operation(summary = "提交活动说明")
    public ApiResponse<ActivityInfo> saveActivity(@PathVariable Long id, @Valid @RequestBody ActivityInfoRequest request) {
        Long applicantId = getCurrentUserId();
        if (isDraftRoute(id, applicantId)) {
            RegistrationDraftActivityInfo activity = registrationDraftService.saveActivity(id, applicantId, request);
            return ApiResponse.ok(registrationDraftCompatService.mapDraftActivity(activity, id));
        }
        request.setRegistrationId(id);
        return ApiResponse.ok(registrationService.saveActivity(request));
    }

    @PutMapping("/{id}/summary")
    @Operation(summary = "提交摘要")
    public ApiResponse<ProjectSummary> saveSummary(@PathVariable Long id, @Valid @RequestBody ProjectSummaryRequest request) {
        Long applicantId = getCurrentUserId();
        if (isDraftRoute(id, applicantId)) {
            RegistrationDraftProjectSummary summary = registrationDraftService.saveSummary(id, applicantId, request);
            return ApiResponse.ok(registrationDraftCompatService.mapSummary(summary, id));
        }
        request.setRegistrationId(id);
        return ApiResponse.ok(registrationService.saveSummary(request));
    }

    @PostMapping("/{id}/submit")
    @Operation(summary = "提交报名")
    public ApiResponse<Registration> submit(@PathVariable Long id) {
        Long applicantId = getCurrentUserId();
        if (isDraftRoute(id, applicantId)) {
            return ApiResponse.ok(registrationDraftService.submit(id, applicantId));
        }
        return ApiResponse.ok(registrationService.submit(id));
    }

    @PostMapping("/{id}/return")
    @Operation(summary = "退回报名")
    public ApiResponse<Registration> returnForEdit(@PathVariable Long id) {
        return ApiResponse.ok(registrationService.returnForEdit(id));
    }

    @GetMapping("/check-duplicate")
    @Operation(summary = "同机构相似项目检测",
               description = "兼容旧参数 selfId：编辑草稿时传 draftId 即可。")
    public ApiResponse<List<java.util.Map<String, Object>>> checkDuplicate(
            @RequestParam Long competitionId,
            @RequestParam Long institutionId,
            @RequestParam String projectName,
            @RequestParam(required = false) Long selfId) {
        return ApiResponse.ok(registrationDraftService.checkDuplicate(
                competitionId, institutionId, projectName, selfId));
    }

    @PostMapping("/{id}/approve")
    @Operation(summary = "通过报名")
    public ApiResponse<Registration> approve(@PathVariable Long id) {
        return ApiResponse.ok(registrationService.approve(id));
    }

    @GetMapping("/{id}")
    @Operation(summary = "报名详情")
    public ApiResponse<RegistrationDetailResponse> detail(@PathVariable Long id) {
        Long applicantId = getCurrentUserId();
        if (isDraftRoute(id, applicantId)) {
            return ApiResponse.ok(registrationDraftCompatService.getDetail(id, applicantId));
        }
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

    @GetMapping("/{id}/published-feedback")
    @Operation(summary = "已发布项目反馈（参赛者端）",
            description = "仅报名申请人可查看；返回组委会最终发布给参赛者的亮点与不足。")
    public ApiResponse<List<ProjectFeedbackItem>> publishedFeedback(@PathVariable Long id) {
        Long applicantId = getCurrentUserId();
        return ApiResponse.ok(reviewService.publishedProjectFeedbacksByRegistration(id, applicantId));
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
    @Operation(summary = "我的报名列表（参赛者端，含草稿与已提交）")
    public ApiResponse<List<MyRegistrationItem>> myRegistrations() {
        Long applicantId = getCurrentUserId();
        List<MyRegistrationItem> items = new ArrayList<>(registrationService.listMyRegistrations(applicantId));
        items.addAll(registrationDraftService.listMyDrafts(applicantId));
        items.sort(Comparator.comparing(
                MyRegistrationItem::getCreatedAt,
                Comparator.nullsLast(Comparator.reverseOrder())));
        return ApiResponse.ok(items);
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

    private boolean isDraftRoute(Long id, Long applicantId) {
        return registrationDraftCompatService.isDraftRoute(id, applicantId);
    }

    @GetMapping("/by-institution")
    @Operation(summary = "按机构查询报名")
    public ApiResponse<List<Registration>> listByInstitution(@RequestParam Long institutionId) {
        return ApiResponse.ok(registrationService.listByInstitution(institutionId));
    }

    @GetMapping("/count-by-institution")
    @Operation(summary = "当前机构在指定赛事的有效报名数（不含已被驳回）")
    public ApiResponse<Long> countByInstitution(@RequestParam Long competitionId) {
        Long applicantId = getCurrentUserId();
        return ApiResponse.ok(registrationService.countByInstitution(competitionId, applicantId));
    }

    @PostMapping("/{id}/materials")
    @Operation(summary = "上传报名材料")
    public ApiResponse<MaterialFile> upload(@PathVariable Long id,
                                            @RequestParam String type,
                                            @RequestPart MultipartFile file) {
        Long applicantId = getCurrentUserId();
        if (isDraftRoute(id, applicantId)) {
            RegistrationDraftMaterialFile material = draftMaterialService.upload(id, type, file);
            return ApiResponse.ok(registrationDraftCompatService.mapMaterial(material, id));
        }
        return ApiResponse.ok(materialService.upload(id, type, file));
    }

    @GetMapping("/{id}/materials")
    @Operation(summary = "报名材料列表")
    public ApiResponse<List<MaterialFile>> listMaterials(@PathVariable Long id) {
        Long applicantId = getCurrentUserId();
        if (isDraftRoute(id, applicantId)) {
            return ApiResponse.ok(registrationDraftCompatService.mapMaterials(
                    draftMaterialService.list(id), id));
        }
        return ApiResponse.ok(materialService.list(id));
    }
}
