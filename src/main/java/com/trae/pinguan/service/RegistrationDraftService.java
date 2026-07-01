package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.ActivityInfo;
import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.domain.entity.MaterialFile;
import com.trae.pinguan.domain.entity.ProjectSummary;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.RegistrationDraft;
import com.trae.pinguan.domain.entity.RegistrationDraftActivityInfo;
import com.trae.pinguan.domain.entity.RegistrationDraftMaterialFile;
import com.trae.pinguan.domain.entity.RegistrationDraftMember;
import com.trae.pinguan.domain.entity.RegistrationDraftProjectSummary;
import com.trae.pinguan.domain.entity.RegistrationMember;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.RegistrationStatus;
import com.trae.pinguan.exception.DuplicateProjectNameException;
import com.trae.pinguan.repository.ActivityInfoRepository;
import com.trae.pinguan.repository.CompetitionRepository;
import com.trae.pinguan.repository.DictionaryItemRepository;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.repository.MaterialFileRepository;
import com.trae.pinguan.repository.ProjectSummaryRepository;
import com.trae.pinguan.repository.RegistrationDraftActivityInfoRepository;
import com.trae.pinguan.repository.RegistrationDraftMaterialFileRepository;
import com.trae.pinguan.repository.RegistrationDraftMemberRepository;
import com.trae.pinguan.repository.RegistrationDraftProjectSummaryRepository;
import com.trae.pinguan.repository.RegistrationDraftRepository;
import com.trae.pinguan.repository.RegistrationMemberRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.ActivityInfoDetailResponse;
import com.trae.pinguan.web.dto.ActivityInfoRequest;
import com.trae.pinguan.web.dto.MemberUpsertRequest;
import com.trae.pinguan.web.dto.MyRegistrationItem;
import com.trae.pinguan.web.dto.ProjectSummaryRequest;
import com.trae.pinguan.web.dto.RegistrationCreateRequest;
import com.trae.pinguan.web.dto.RegistrationDraftDetailResponse;
import com.trae.pinguan.web.dto.RegistrationUpdateRequest;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class RegistrationDraftService {
    private static final String PAYMENT_PROOF_TYPE = "payment_proof";
    private static final String REGISTRATION_FORM_DOC_TYPE = "REGISTRATION_FORM_DOC";
    private static final String REGISTRATION_FORM_PDF_TYPE = "REGISTRATION_FORM_PDF";

    private final RegistrationDraftRepository draftRepository;
    private final RegistrationDraftMemberRepository draftMemberRepository;
    private final RegistrationDraftActivityInfoRepository draftActivityRepository;
    private final RegistrationDraftProjectSummaryRepository draftSummaryRepository;
    private final RegistrationDraftMaterialFileRepository draftMaterialRepository;
    private final RegistrationRepository registrationRepository;
    private final RegistrationMemberRepository memberRepository;
    private final ActivityInfoRepository activityInfoRepository;
    private final ProjectSummaryRepository summaryRepository;
    private final MaterialFileRepository materialRepository;
    private final CompetitionRepository competitionRepository;
    private final InstitutionRepository institutionRepository;
    private final UserAccountRepository userAccountRepository;
    private final DictionaryItemRepository dictionaryItemRepository;
    private final RegistrationService registrationService;

    @Transactional
    public RegistrationDraft create(RegistrationCreateRequest request) {
        Competition competition = competitionRepository.findById(request.getCompetitionId())
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        UserAccount applicant = userAccountRepository.findById(request.getApplicantId())
                .orElseThrow(() -> new IllegalArgumentException("报名人不存在"));

        Institution institution;
        if (request.getInstitutionId() != null) {
            institution = institutionRepository.findById(request.getInstitutionId())
                    .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
        } else {
            institution = applicant.getInstitution();
            if (institution == null) {
                throw new IllegalArgumentException("用户未绑定机构，无法创建报名草稿");
            }
        }
        validateBasicGroupEligibility(institution, request.getGroupType());

        LocalDateTime now = LocalDateTime.now();
        RegistrationDraft draft = RegistrationDraft.builder()
                .competition(competition)
                .institution(institution)
                .applicant(applicant)
                .projectName(request.getProjectName())
                .groupType(request.getGroupType())
                .createdAt(now)
                .updatedAt(now)
                .build();
        return draftRepository.save(draft);
    }

    @Transactional
    public RegistrationDraft update(Long draftId, Long applicantId, RegistrationUpdateRequest request) {
        RegistrationDraft draft = requireOwnedDraft(draftId, applicantId);
        if (request.getProjectName() != null) {
            draft.setProjectName(request.getProjectName());
        }
        if (request.getGroupType() != null) {
            draft.setGroupType(request.getGroupType());
        }
        if (request.getInstitutionId() != null) {
            Institution institution = institutionRepository.findById(request.getInstitutionId())
                    .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
            draft.setInstitution(institution);
        }
        if (request.getProjectLeaderName() != null) {
            draft.setProjectLeaderName(request.getProjectLeaderName());
        }
        if (request.getProjectLeaderPhone() != null) {
            draft.setProjectLeaderPhone(request.getProjectLeaderPhone());
        }
        if (request.getProjectLeaderTitle() != null) {
            draft.setProjectLeaderTitle(request.getProjectLeaderTitle());
        }
        validateBasicGroupEligibility(draft.getInstitution(), draft.getGroupType());
        draft.setUpdatedAt(LocalDateTime.now());
        return draftRepository.save(draft);
    }

    @Transactional
    public List<RegistrationDraftMember> upsertMembers(Long draftId, Long applicantId, MemberUpsertRequest request) {
        RegistrationDraft draft = requireOwnedDraft(draftId, applicantId);
        if (request.getMembers().size() > 20) {
            throw new IllegalArgumentException("人员数量超限");
        }
        draftMemberRepository.deleteByDraftId(draftId);
        List<RegistrationDraftMember> members = request.getMembers().stream()
                .map(item -> RegistrationDraftMember.builder()
                        .draft(draft)
                        .role(item.getRole())
                        .name(item.getName())
                        .title(item.getTitle())
                        .department(item.getDepartment())
                        .build())
                .collect(Collectors.toList());
        draft.setUpdatedAt(LocalDateTime.now());
        draftRepository.save(draft);
        return draftMemberRepository.saveAll(members);
    }

    @Transactional
    public RegistrationDraftActivityInfo saveActivity(Long draftId, Long applicantId, ActivityInfoRequest request) {
        RegistrationDraft draft = requireOwnedDraft(draftId, applicantId);
        RegistrationDraftActivityInfo activity = draftActivityRepository.findByDraftId(draftId)
                .orElse(RegistrationDraftActivityInfo.builder().draft(draft).build());
        activity.setTheme(request.getTheme());
        activity.setKeywords(request.getKeywords());
        activity.setSubjectTypeCode(request.getSubjectTypeCode());
        activity.setSubjectTypeOther(request.getSubjectTypeOther());
        activity.setMethodCode(request.getMethodCode());
        activity.setMethodOther(request.getMethodOther());
        activity.setExperienceImproveCode(request.getExperienceImproveCode());
        activity.setExperienceImproveOther(request.getExperienceImproveOther());
        activity.setQualityTopicCode(request.getQualityTopicCode());
        activity.setQualityTopicOther(request.getQualityTopicOther());
        activity.setAvgWorkYears(request.getAvgWorkYears());
        activity.setAvgAge(request.getAvgAge());
        activity.setCrossDepartment(request.getCrossDepartment());
        activity.setRelatedToDigitalAi(request.getRelatedToDigitalAi());
        draft.setUpdatedAt(LocalDateTime.now());
        draftRepository.save(draft);
        return draftActivityRepository.save(activity);
    }

    @Transactional
    public RegistrationDraftProjectSummary saveSummary(Long draftId, Long applicantId, ProjectSummaryRequest request) {
        RegistrationDraft draft = requireOwnedDraft(draftId, applicantId);
        RegistrationDraftProjectSummary summary = draftSummaryRepository.findByDraftId(draftId)
                .orElse(RegistrationDraftProjectSummary.builder().draft(draft).build());
        summary.setTheme(request.getTheme());
        summary.setPlan(request.getPlan());
        summary.setProblem(request.getProblem());
        summary.setAction(request.getAction());
        summary.setSuccess(request.getSuccess());
        summary.setDiscussion(request.getDiscussion());
        summary.setOperation(request.getOperation());
        summary.setPresentation(request.getPresentation());
        draft.setUpdatedAt(LocalDateTime.now());
        draftRepository.save(draft);
        return draftSummaryRepository.save(summary);
    }

    @Transactional
    public Registration submit(Long draftId, Long applicantId) {
        RegistrationDraft draft = requireOwnedDraft(draftId, applicantId);

        if (draft.getInstitution() != null && draft.getProjectName() != null) {
            List<Map<String, Object>> hits = checkDuplicate(
                    draft.getCompetition().getId(),
                    draft.getInstitution().getId(),
                    draft.getProjectName(),
                    draftId);
            List<Map<String, Object>> blocked = hits.stream()
                    .filter(h -> ((Number) h.get("similarity")).doubleValue() >= 80.0)
                    .collect(Collectors.toList());
            if (!blocked.isEmpty()) {
                throw new DuplicateProjectNameException(blocked);
            }
        }
        validateRequiredMaterialsBeforeSubmit(draftId);

        LocalDateTime now = LocalDateTime.now();
        Registration registration = Registration.builder()
                .competition(draft.getCompetition())
                .institution(draft.getInstitution())
                .applicant(draft.getApplicant())
                .projectName(draft.getProjectName())
                .groupType(draft.getGroupType())
                .status(RegistrationStatus.SUBMITTED)
                .submittedAt(now)
                .createdAt(now)
                .projectLeaderName(draft.getProjectLeaderName())
                .projectLeaderPhone(draft.getProjectLeaderPhone())
                .projectLeaderTitle(draft.getProjectLeaderTitle())
                .build();
        registration = registrationRepository.save(registration);
        final Registration savedRegistration = registration;

        for (RegistrationDraftMember dm : draftMemberRepository.findByDraftId(draftId)) {
            memberRepository.save(RegistrationMember.builder()
                    .registration(savedRegistration)
                    .role(dm.getRole())
                    .name(dm.getName())
                    .title(dm.getTitle())
                    .department(dm.getDepartment())
                    .build());
        }

        draftActivityRepository.findByDraftId(draftId).ifPresent(da ->
                activityInfoRepository.save(ActivityInfo.builder()
                        .registration(savedRegistration)
                        .theme(da.getTheme())
                        .keywords(da.getKeywords())
                        .subjectTypeCode(da.getSubjectTypeCode())
                        .subjectTypeOther(da.getSubjectTypeOther())
                        .methodCode(da.getMethodCode())
                        .methodOther(da.getMethodOther())
                        .experienceImproveCode(da.getExperienceImproveCode())
                        .experienceImproveOther(da.getExperienceImproveOther())
                        .qualityTopicCode(da.getQualityTopicCode())
                        .qualityTopicOther(da.getQualityTopicOther())
                        .avgWorkYears(da.getAvgWorkYears())
                        .avgAge(da.getAvgAge())
                        .crossDepartment(da.getCrossDepartment())
                        .relatedToDigitalAi(da.getRelatedToDigitalAi())
                        .build()));

        draftSummaryRepository.findByDraftId(draftId).ifPresent(ds ->
                summaryRepository.save(ProjectSummary.builder()
                        .registration(savedRegistration)
                        .theme(ds.getTheme())
                        .plan(ds.getPlan())
                        .problem(ds.getProblem())
                        .action(ds.getAction())
                        .success(ds.getSuccess())
                        .discussion(ds.getDiscussion())
                        .operation(ds.getOperation())
                        .presentation(ds.getPresentation())
                        .build()));

        for (RegistrationDraftMaterialFile dm : draftMaterialRepository.findByDraftId(draftId)) {
            materialRepository.save(MaterialFile.builder()
                    .registration(savedRegistration)
                    .type(dm.getType())
                    .fileName(dm.getFileName())
                    .fileUrl(dm.getFileUrl())
                    .fileHash(dm.getFileHash())
                    .uploadedAt(dm.getUploadedAt())
                    .build());
        }

        deleteDraftData(draftId);
        log.info("草稿 {} 已提交为正式报名 id={}", draftId, registration.getId());
        return registration;
    }

    @Transactional
    public void deleteDraft(Long draftId, Long applicantId) {
        requireOwnedDraft(draftId, applicantId);
        deleteDraftData(draftId);
    }

    @Transactional(readOnly = true)
    public RegistrationDraftDetailResponse getDetail(Long draftId, Long applicantId) {
        RegistrationDraft draft = requireOwnedDraft(draftId, applicantId);
        Institution institution = draft.getInstitution();
        com.trae.pinguan.web.dto.InstitutionInfo institutionInfo = null;
        if (institution != null) {
            institutionInfo = com.trae.pinguan.web.dto.InstitutionInfo.builder()
                    .id(institution.getId())
                    .name(institution.getName())
                    .code(institution.getCode())
                    .uscc(institution.getUscc())
                    .region(institution.getRegion())
                    .level(institution.getLevel())
                    .build();
        }

        List<RegistrationDraftMember> members = draftMemberRepository.findByDraftId(draftId);
        RegistrationDraftActivityInfo activity = draftActivityRepository.findByDraftId(draftId).orElse(null);
        RegistrationDraftProjectSummary summary = draftSummaryRepository.findByDraftId(draftId).orElse(null);
        List<RegistrationDraftMaterialFile> allMaterials = draftMaterialRepository.findByDraftId(draftId);
        List<RegistrationDraftMaterialFile> paymentProofs = allMaterials.stream()
                .filter(m -> PAYMENT_PROOF_TYPE.equalsIgnoreCase(m.getType()))
                .collect(Collectors.toList());
        List<RegistrationDraftMaterialFile> materials = allMaterials.stream()
                .filter(m -> !PAYMENT_PROOF_TYPE.equalsIgnoreCase(m.getType()))
                .collect(Collectors.toList());

        ActivityInfoDetailResponse activityDetail = null;
        if (activity != null) {
            activityDetail = new ActivityInfoDetailResponse(
                    activity.getTheme(),
                    activity.getKeywords(),
                    activity.getSubjectTypeCode(),
                    activity.getSubjectTypeOther(),
                    labelOf(activity.getSubjectTypeCode()),
                    activity.getMethodCode(),
                    activity.getMethodOther(),
                    labelOf(activity.getMethodCode()),
                    activity.getExperienceImproveCode(),
                    activity.getExperienceImproveOther(),
                    labelOf(activity.getExperienceImproveCode()),
                    activity.getQualityTopicCode(),
                    activity.getQualityTopicOther(),
                    labelOf(activity.getQualityTopicCode()),
                    activity.getAvgWorkYears(),
                    activity.getAvgAge(),
                    activity.getCrossDepartment(),
                    activity.getRelatedToDigitalAi());
        }

        Long competitionId = null;
        String competitionName = null;
        if (draft.getCompetition() != null) {
            competitionId = draft.getCompetition().getId();
            competitionName = draft.getCompetition().getName();
        }

        return RegistrationDraftDetailResponse.builder()
                .draft(draft)
                .competitionId(competitionId)
                .competitionName(competitionName)
                .institution(institutionInfo)
                .members(members)
                .activityInfo(activityDetail)
                .projectSummary(summary)
                .materials(materials)
                .paymentProofs(paymentProofs)
                .build();
    }

    @Transactional(readOnly = true)
    public List<MyRegistrationItem> listMyDrafts(Long applicantId) {
        return listMyDrafts(applicantId, null);
    }

    @Transactional(readOnly = true)
    public List<MyRegistrationItem> listMyDrafts(Long applicantId, Long competitionId) {
        return draftRepository.findByApplicantIdOrderByUpdatedAtDesc(applicantId).stream()
                .filter(draft -> competitionId == null
                        || (draft.getCompetition() != null
                        && competitionId.equals(draft.getCompetition().getId())))
                .map(draft -> {
                    Institution institution = draft.getInstitution();
                    Competition competition = draft.getCompetition();
                    return MyRegistrationItem.builder()
                            .id(draft.getId())
                            .draft(true)
                            .projectName(draft.getProjectName())
                            .groupType(draft.getGroupType())
                            .status(RegistrationStatus.DRAFT)
                            .submittedAt(null)
                            .createdAt(draft.getCreatedAt())
                            .institutionId(institution != null ? institution.getId() : null)
                            .institutionName(institution != null ? institution.getName() : null)
                            .institutionLevel(institution != null ? institution.getLevel() : null)
                            .competitionId(competition != null ? competition.getId() : null)
                            .competitionName(competition != null ? competition.getName() : null)
                            .build();
                })
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> checkDuplicate(Long competitionId, Long institutionId,
                                                     String projectName, Long selfDraftId) {
        List<Map<String, Object>> results = new ArrayList<>(
                registrationService.checkDuplicate(competitionId, institutionId, projectName, null));
        if (projectName == null || projectName.trim().isEmpty()) {
            return results;
        }
        for (RegistrationDraft other : draftRepository.findByCompetition_IdAndInstitution_Id(
                competitionId, institutionId)) {
            if (selfDraftId != null && selfDraftId.equals(other.getId())) {
                continue;
            }
            double sim = registrationService.projectNameSimilarityPercent(projectName, other.getProjectName());
            if (sim >= 50.0) {
                Map<String, Object> item = new LinkedHashMap<>();
                item.put("draftId", other.getId());
                item.put("draft", true);
                item.put("projectName", other.getProjectName());
                item.put("similarity", sim);
                results.add(item);
            }
        }
        results.sort((a, b) -> Double.compare(
                ((Number) b.get("similarity")).doubleValue(),
                ((Number) a.get("similarity")).doubleValue()));
        return results.stream().limit(5).collect(Collectors.toList());
    }

    public void verifyOwnership(Long draftId, Long applicantId) {
        requireOwnedDraft(draftId, applicantId);
    }

    private RegistrationDraft requireOwnedDraft(Long draftId, Long applicantId) {
        RegistrationDraft draft = draftRepository.findById(draftId)
                .orElseThrow(() -> new IllegalArgumentException("草稿不存在"));
        if (draft.getApplicant() == null || !draft.getApplicant().getId().equals(applicantId)) {
            throw new IllegalArgumentException("无权操作该草稿");
        }
        return draft;
    }

    private void deleteDraftData(Long draftId) {
        draftMemberRepository.deleteByDraftId(draftId);
        draftActivityRepository.deleteByDraftId(draftId);
        draftSummaryRepository.deleteByDraftId(draftId);
        draftMaterialRepository.deleteByDraftId(draftId);
        draftRepository.deleteById(draftId);
    }

    private void validateRequiredMaterialsBeforeSubmit(Long draftId) {
        List<RegistrationDraftMaterialFile> files = draftMaterialRepository.findByDraftId(draftId);
        boolean hasRegFormDoc = files.stream()
                .anyMatch(m -> REGISTRATION_FORM_DOC_TYPE.equalsIgnoreCase(m.getType()));
        boolean hasRegFormPdf = files.stream()
                .anyMatch(m -> REGISTRATION_FORM_PDF_TYPE.equalsIgnoreCase(m.getType()));
        if (!hasRegFormDoc || !hasRegFormPdf) {
            throw new IllegalArgumentException("提交前需同时上传报名表Word和PDF（盖章扫描件）");
        }
    }

    private void validateBasicGroupEligibility(Institution institution, GroupType groupType) {
        if (institution == null || groupType == null) {
            return;
        }
        if (groupType == GroupType.BASIC) {
            String level = institution.getLevel() == null ? "" : institution.getLevel().trim();
            if (level.startsWith("三级")) {
                throw new IllegalArgumentException("三级医疗机构不可选择基层组，请选择综合组或进阶组");
            }
        }
    }

    private String labelOf(String code) {
        if (code == null || code.trim().isEmpty()) {
            return null;
        }
        return dictionaryItemRepository.findFirstByCode(code)
                .map(item -> item.getLabel())
                .orElse(code);
    }
}
