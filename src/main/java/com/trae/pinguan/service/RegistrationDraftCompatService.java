package com.trae.pinguan.service;

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
import com.trae.pinguan.domain.enums.RegistrationStatus;
import com.trae.pinguan.repository.RegistrationDraftRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.web.dto.ActivityInfoDetailResponse;
import com.trae.pinguan.web.dto.RegistrationDetailResponse;
import com.trae.pinguan.web.dto.RegistrationDraftDetailResponse;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 旧 /api/registrations/** 与草稿体系的过渡兼容：id 在正式表不存在时，按草稿 id 处理。
 */
@Service
@RequiredArgsConstructor
public class RegistrationDraftCompatService {
    private final RegistrationRepository registrationRepository;
    private final RegistrationDraftRepository draftRepository;
    private final RegistrationDraftService draftService;

    @Transactional(readOnly = true)
    public boolean isDraftRoute(Long id, Long applicantId) {
        if (registrationRepository.existsById(id)) {
            return false;
        }
        return draftRepository.findById(id)
                .filter(d -> d.getApplicant() != null && d.getApplicant().getId().equals(applicantId))
                .isPresent();
    }

    @Transactional(readOnly = true)
    public RegistrationDetailResponse getDetail(Long id, Long applicantId) {
        RegistrationDraftDetailResponse draftDetail = draftService.getDetail(id, applicantId);
        return toRegistrationDetail(draftDetail);
    }

    public Registration asRegistrationView(RegistrationDraft draft) {
        return Registration.builder()
                .id(draft.getId())
                .competition(draft.getCompetition())
                .institution(draft.getInstitution())
                .applicant(draft.getApplicant())
                .projectName(draft.getProjectName())
                .groupType(draft.getGroupType())
                .status(RegistrationStatus.DRAFT)
                .createdAt(draft.getCreatedAt())
                .projectLeaderName(draft.getProjectLeaderName())
                .projectLeaderPhone(draft.getProjectLeaderPhone())
                .projectLeaderTitle(draft.getProjectLeaderTitle())
                .build();
    }

    public List<RegistrationMember> mapMembers(List<RegistrationDraftMember> draftMembers, Long viewId) {
        return draftMembers.stream()
                .map(m -> RegistrationMember.builder()
                        .id(m.getId())
                        .registrationId(viewId)
                        .role(m.getRole())
                        .name(m.getName())
                        .title(m.getTitle())
                        .department(m.getDepartment())
                        .build())
                .collect(Collectors.toList());
    }

    public MaterialFile mapMaterial(RegistrationDraftMaterialFile m, Long viewId) {
        return MaterialFile.builder()
                .id(m.getId())
                .registrationId(viewId)
                .type(m.getType())
                .fileName(m.getFileName())
                .fileUrl(m.getFileUrl())
                .fileHash(m.getFileHash())
                .uploadedAt(m.getUploadedAt())
                .build();
    }

    public List<MaterialFile> mapMaterials(List<RegistrationDraftMaterialFile> files, Long viewId) {
        return files.stream().map(f -> mapMaterial(f, viewId)).collect(Collectors.toList());
    }

    public ProjectSummary mapSummary(RegistrationDraftProjectSummary s, Long viewId) {
        if (s == null) {
            return null;
        }
        return ProjectSummary.builder()
                .id(s.getId())
                .theme(s.getTheme())
                .plan(s.getPlan())
                .problem(s.getProblem())
                .action(s.getAction())
                .success(s.getSuccess())
                .discussion(s.getDiscussion())
                .operation(s.getOperation())
                .presentation(s.getPresentation())
                .build();
    }

    public ActivityInfo mapDraftActivity(RegistrationDraftActivityInfo da, Long viewId) {
        if (da == null) {
            return null;
        }
        return ActivityInfo.builder()
                .id(da.getId())
                .registrationId(viewId)
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
                .build();
    }

    public ActivityInfo mapActivity(ActivityInfoDetailResponse a, Long viewId) {
        if (a == null) {
            return null;
        }
        return ActivityInfo.builder()
                .registrationId(viewId)
                .theme(a.getTheme())
                .keywords(a.getKeywords())
                .subjectTypeCode(a.getSubjectTypeCode())
                .subjectTypeOther(a.getSubjectTypeOther())
                .methodCode(a.getMethodCode())
                .methodOther(a.getMethodOther())
                .experienceImproveCode(a.getExperienceImproveCode())
                .experienceImproveOther(a.getExperienceImproveOther())
                .qualityTopicCode(a.getQualityTopicCode())
                .qualityTopicOther(a.getQualityTopicOther())
                .avgWorkYears(a.getAvgWorkYears())
                .avgAge(a.getAvgAge())
                .crossDepartment(a.getCrossDepartment())
                .relatedToDigitalAi(a.getRelatedToDigitalAi())
                .build();
    }

    private RegistrationDetailResponse toRegistrationDetail(RegistrationDraftDetailResponse draftDetail) {
        RegistrationDraft draft = draftDetail.getDraft();
        Long viewId = draft.getId();
        return RegistrationDetailResponse.builder()
                .draft(true)
                .registration(asRegistrationView(draft))
                .competitionId(draftDetail.getCompetitionId())
                .competitionName(draftDetail.getCompetitionName())
                .institution(draftDetail.getInstitution())
                .members(draftDetail.getMembers() == null ? java.util.Collections.emptyList()
                        : mapMembers(draftDetail.getMembers(), viewId))
                .activityInfo(draftDetail.getActivityInfo())
                .projectSummary(mapSummary(draftDetail.getProjectSummary(), viewId))
                .materials(mapMaterials(draftDetail.getMaterials(), viewId))
                .paymentProofs(mapMaterials(draftDetail.getPaymentProofs(), viewId))
                .build();
    }
}
