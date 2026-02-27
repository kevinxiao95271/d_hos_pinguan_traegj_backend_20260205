package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.ActivityInfo;
import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.domain.entity.MaterialFile;
import com.trae.pinguan.domain.entity.ProjectSummary;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.RegistrationMember;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.RegistrationStatus;
import com.trae.pinguan.repository.ActivityInfoRepository;
import com.trae.pinguan.repository.CompetitionRepository;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.repository.MaterialFileRepository;
import com.trae.pinguan.repository.ProjectSummaryRepository;
import com.trae.pinguan.repository.RegistrationMemberRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.repository.ReviewTaskRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.ActivityInfoRequest;
import com.trae.pinguan.web.dto.ActivityInfoDetailResponse;
import com.trae.pinguan.web.dto.AutoGroupRequest;
import com.trae.pinguan.web.dto.BatchClassificationRequest;
import com.trae.pinguan.web.dto.GroupedRegistrationItem;
import com.trae.pinguan.web.dto.GroupedRegistrationResponse;
import com.trae.pinguan.web.dto.MemberUpsertRequest;
import com.trae.pinguan.web.dto.ProjectSummaryRequest;
import com.trae.pinguan.web.dto.RegistrationFilterItem;
import com.trae.pinguan.web.dto.RegistrationCreateRequest;
import com.trae.pinguan.web.dto.RegistrationDetailResponse;
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
public class RegistrationService {
    private final RegistrationRepository registrationRepository;
    private final RegistrationMemberRepository memberRepository;
    private final CompetitionRepository competitionRepository;
    private final InstitutionRepository institutionRepository;
    private final com.trae.pinguan.repository.DictionaryItemRepository dictionaryItemRepository;
    private final UserAccountRepository userAccountRepository;
    private final ActivityInfoRepository activityInfoRepository;
    private final ProjectSummaryRepository summaryRepository;
    private final MaterialFileRepository materialRepository;
    private final ReviewTaskRepository reviewTaskRepository;

    @Transactional
    public Registration create(RegistrationCreateRequest request) {
        Competition competition = competitionRepository.findById(request.getCompetitionId())
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        
        UserAccount applicant = userAccountRepository.findById(request.getApplicantId())
                .orElseThrow(() -> new IllegalArgumentException("报名人不存在"));
        
        // 机构ID：如果前端未传，则自动使用申请人的所属机构
        Institution institution;
        if (request.getInstitutionId() != null) {
            // 前端指定了机构（特殊情况，如代表其他机构报名）
            institution = institutionRepository.findById(request.getInstitutionId())
                    .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
            log.info("创建报名：用户 {} 代表机构 {} 报名", applicant.getName(), institution.getName());
        } else {
            // 自动使用申请人的所属机构
            institution = applicant.getInstitution();
            if (institution == null) {
                throw new IllegalArgumentException("用户未绑定机构，无法创建报名");
            }
            log.info("创建报名：用户 {} 使用所属机构 {} 报名", applicant.getName(), institution.getName());
        }
        
        Registration registration = Registration.builder()
                .competition(competition)
                .institution(institution)
                .applicant(applicant)
                .projectName(request.getProjectName())
                .groupType(request.getGroupType())
                .status(RegistrationStatus.DRAFT)
                .createdAt(LocalDateTime.now())
                .build();
        return registrationRepository.save(registration);
    }

    @Transactional
    public Registration update(Long id, com.trae.pinguan.web.dto.RegistrationUpdateRequest request) {
        Registration registration = registrationRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        // 只有草稿或退回状态才能修改基本信息
        if (registration.getStatus() != RegistrationStatus.DRAFT 
                && registration.getStatus() != RegistrationStatus.RETURNED) {
            throw new IllegalArgumentException("当前状态不允许修改");
        }
        if (request.getProjectName() != null) {
            registration.setProjectName(request.getProjectName());
        }
        if (request.getGroupType() != null) {
            registration.setGroupType(request.getGroupType());
        }
        if (request.getInstitutionId() != null) {
            Institution institution = institutionRepository.findById(request.getInstitutionId())
                    .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
            registration.setInstitution(institution);
        }
        return registrationRepository.save(registration);
    }

    @Transactional
    public List<RegistrationMember> upsertMembers(MemberUpsertRequest request) {
        Registration registration = registrationRepository.findById(request.getRegistrationId())
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        if (request.getMembers().size() > 20) {
            throw new IllegalArgumentException("人员数量超限");
        }
        List<RegistrationMember> existing = memberRepository.findByRegistrationId(registration.getId());
        memberRepository.deleteAll(existing);
        List<RegistrationMember> members = request.getMembers().stream()
                .map(item -> RegistrationMember.builder()
                        .registration(registration)
                        .role(item.getRole())
                        .name(item.getName())
                        .title(item.getTitle())
                        .department(item.getDepartment())
                        .build())
                .collect(Collectors.toList());
        return memberRepository.saveAll(members);
    }

    @Transactional
    public ActivityInfo saveActivity(ActivityInfoRequest request) {
        Registration registration = registrationRepository.findById(request.getRegistrationId())
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        ActivityInfo activityInfo = activityInfoRepository.findByRegistrationId(registration.getId())
                .orElse(ActivityInfo.builder().registration(registration).build());
        activityInfo.setTheme(request.getTheme());
        activityInfo.setKeywords(request.getKeywords());
        activityInfo.setSubjectTypeCode(request.getSubjectTypeCode());
        activityInfo.setSubjectTypeOther(request.getSubjectTypeOther());
        activityInfo.setMethodCode(request.getMethodCode());
        activityInfo.setMethodOther(request.getMethodOther());
        activityInfo.setExperienceImproveCode(request.getExperienceImproveCode());
        activityInfo.setExperienceImproveOther(request.getExperienceImproveOther());
        activityInfo.setQualityTopicCode(request.getQualityTopicCode());
        activityInfo.setQualityTopicOther(request.getQualityTopicOther());
        activityInfo.setAvgWorkYears(request.getAvgWorkYears());
        activityInfo.setAvgAge(request.getAvgAge());
        activityInfo.setCrossDepartment(request.getCrossDepartment());
        activityInfo.setRelatedToDigitalAi(request.getRelatedToDigitalAi());
        return activityInfoRepository.save(activityInfo);
    }

    @Transactional
    public ProjectSummary saveSummary(ProjectSummaryRequest request) {
        Registration registration = registrationRepository.findById(request.getRegistrationId())
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        ProjectSummary summary = summaryRepository.findByRegistrationId(registration.getId())
                .orElse(ProjectSummary.builder().registration(registration).build());
        summary.setTheme(request.getTheme());
        summary.setPlan(request.getPlan());
        summary.setProblem(request.getProblem());
        summary.setAction(request.getAction());
        summary.setSuccess(request.getSuccess());
        summary.setDiscussion(request.getDiscussion());
        summary.setOperation(request.getOperation());
        summary.setPresentation(request.getPresentation());
        return summaryRepository.save(summary);
    }

    @Transactional
    public Registration submit(Long registrationId) {
        Registration registration = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        registration.setStatus(RegistrationStatus.SUBMITTED);
        registration.setSubmittedAt(LocalDateTime.now());
        return registrationRepository.save(registration);
    }

    @Transactional
    public Registration returnForEdit(Long registrationId) {
        Registration registration = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        Competition competition = registration.getCompetition();
        if (competition.getRegisterEnd() != null && LocalDateTime.now().isAfter(competition.getRegisterEnd())) {
            throw new IllegalArgumentException("报名已截止");
        }
        boolean scored = reviewTaskRepository.findByRegistrationId(registrationId).stream()
                .anyMatch(task -> task.getStatus() == com.trae.pinguan.domain.enums.ReviewStatus.SCORED);
        if (scored) {
            throw new IllegalArgumentException("已评分无法退回");
        }
        registration.setStatus(RegistrationStatus.RETURNED);
        return registrationRepository.save(registration);
    }

    @Transactional
    public Registration approve(Long registrationId) {
        Registration registration = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        registration.setStatus(RegistrationStatus.APPROVED);
        return registrationRepository.save(registration);
    }

    @Transactional(readOnly = true)
    public RegistrationDetailResponse getDetail(Long registrationId) {
        Registration registration = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        
        // 获取机构详细信息
        com.trae.pinguan.web.dto.InstitutionInfo institutionInfo = null;
        if (registration.getInstitution() != null) {
            Institution inst = registration.getInstitution();
            institutionInfo = com.trae.pinguan.web.dto.InstitutionInfo.builder()
                    .id(inst.getId())
                    .name(inst.getName())
                    .code(inst.getCode())
                    .uscc(inst.getUscc())
                    .region(inst.getRegion())
                    .level(inst.getLevel())
                    .build();
        }
        
        List<RegistrationMember> members = memberRepository.findByRegistrationId(registrationId);
        ActivityInfo activity = activityInfoRepository.findByRegistrationId(registrationId).orElse(null);
        ProjectSummary summary = summaryRepository.findByRegistrationId(registrationId).orElse(null);
        List<MaterialFile> materials = materialRepository.findByRegistrationId(registrationId);
        ActivityInfoDetailResponse activityDetail = null;
        if (activity != null) {
            String methodLabel = null;
            String subjectTypeLabel = null;
            String experienceImproveLabel = null;
            String qualityTopicLabel = null;
            
            // 字典标签查询已移除，直接使用code作为label
            if (activity.getMethodCode() != null && !activity.getMethodCode().trim().isEmpty()) {
                methodLabel = activity.getMethodCode();
            }
            if (activity.getSubjectTypeCode() != null && !activity.getSubjectTypeCode().trim().isEmpty()) {
                subjectTypeLabel = activity.getSubjectTypeCode();
            }
            if (activity.getExperienceImproveCode() != null && !activity.getExperienceImproveCode().trim().isEmpty()) {
                experienceImproveLabel = activity.getExperienceImproveCode();
            }
            if (activity.getQualityTopicCode() != null && !activity.getQualityTopicCode().trim().isEmpty()) {
                qualityTopicLabel = activity.getQualityTopicCode();
            }
            activityDetail = new ActivityInfoDetailResponse(
                    activity.getTheme(),
                    activity.getKeywords(),
                    activity.getSubjectTypeCode(),
                    activity.getSubjectTypeOther(),
                    subjectTypeLabel,
                    activity.getMethodCode(),
                    activity.getMethodOther(),
                    methodLabel,
                    activity.getExperienceImproveCode(),
                    activity.getExperienceImproveOther(),
                    experienceImproveLabel,
                    activity.getQualityTopicCode(),
                    activity.getQualityTopicOther(),
                    qualityTopicLabel,
                    activity.getAvgWorkYears(),
                    activity.getAvgAge(),
                    activity.getCrossDepartment(),
                    activity.getRelatedToDigitalAi()
            );
        }
        // 获取赛事信息
        Long competitionId = null;
        String competitionName = null;
        if (registration.getCompetition() != null) {
            Competition comp = registration.getCompetition();
            competitionId = comp.getId();
            competitionName = comp.getName();
        }
        
        return RegistrationDetailResponse.builder()
                .registration(registration)
                .competitionId(competitionId)
                .competitionName(competitionName)
                .institution(institutionInfo)
                .members(members)
                .activityInfo(activityDetail)
                .projectSummary(summary)
                .materials(materials)
                .build();
    }

    public List<Registration> listByCompetition(Long competitionId) {
        return registrationRepository.findByCompetitionId(competitionId);
    }

    public List<Registration> listByCompetitionAndStatus(Long competitionId, RegistrationStatus status) {
        return registrationRepository.findByCompetitionIdAndStatus(competitionId, status);
    }

    public List<Registration> listByApplicant(Long applicantId) {
        return registrationRepository.findByApplicantId(applicantId);
    }

    @Transactional(readOnly = true)
    public List<com.trae.pinguan.web.dto.MyRegistrationItem> listMyRegistrations(Long applicantId) {
        List<Registration> registrations = registrationRepository.findByApplicantId(applicantId);
        
        return registrations.stream()
                .map(reg -> {
                    Institution institution = reg.getInstitution();
                    Competition competition = reg.getCompetition();
                    
                    return com.trae.pinguan.web.dto.MyRegistrationItem.builder()
                            .id(reg.getId())
                            .projectName(reg.getProjectName())
                            .groupType(reg.getGroupType())
                            .groupCode(reg.getGroupCode())
                            .status(reg.getStatus())
                            .submittedAt(reg.getSubmittedAt())
                            .createdAt(reg.getCreatedAt())
                            // 机构信息
                            .institutionId(institution != null ? institution.getId() : null)
                            .institutionName(institution != null ? institution.getName() : null)
                            .institutionLevel(institution != null ? institution.getLevel() : null)
                            // 赛事信息
                            .competitionId(competition != null ? competition.getId() : null)
                            .competitionName(competition != null ? competition.getName() : null)
                            .build();
                })
                .collect(Collectors.toList());
    }

    public List<Registration> listByInstitution(Long institutionId) {
        return registrationRepository.findByInstitutionId(institutionId);
    }

    public List<RegistrationFilterItem> filterRegistrations(Long competitionId,
                                                            com.trae.pinguan.domain.enums.GroupType groupType,
                                                            String groupCode,
                                                            String projectName,
                                                            String institutionName,
                                                            String methodCode,
                                                            String subjectTypeCode) {
        String groupCodeValue = groupCode == null || groupCode.trim().isEmpty() ? null : groupCode.trim();
        String projectNameValue = projectName == null || projectName.trim().isEmpty() ? null : projectName.trim();
        String institutionNameValue = institutionName == null || institutionName.trim().isEmpty() ? null : institutionName.trim();
        String methodCodeValue = methodCode == null || methodCode.trim().isEmpty() ? null : methodCode.trim();
        String subjectTypeCodeValue = subjectTypeCode == null || subjectTypeCode.trim().isEmpty() ? null : subjectTypeCode.trim();
        List<RegistrationFilterItem> items = registrationRepository.filterRegistrations(
                competitionId,
                groupType,
                groupCodeValue,
                projectNameValue,
                institutionNameValue,
                methodCodeValue,
                subjectTypeCodeValue
        );
        if (items.isEmpty()) {
            return items;
        }
        // 从字典表查询label
        for (RegistrationFilterItem item : items) {
            if (item.getMethodCode() != null) {
                item.setMethodLabel(getLabel(item.getMethodCode()));
            }
            if (item.getSubjectTypeCode() != null) {
                item.setSubjectTypeLabel(getLabel(item.getSubjectTypeCode()));
            }
        }
        return items;
    }

    @Transactional
    public List<Registration> batchClassify(BatchClassificationRequest request) {
        List<Registration> registrations = registrationRepository.findAllById(request.getRegistrationIds());
        for (Registration registration : registrations) {
            registration.setGroupCode(request.getGroupCode());
        }
        return registrationRepository.saveAll(registrations);
    }

    @Transactional
    public List<Registration> autoGroup(AutoGroupRequest request) {
        List<Registration> registrations = request.getStatus() == null
                ? registrationRepository.findByCompetitionId(request.getCompetitionId())
                : registrationRepository.findByCompetitionIdAndStatus(request.getCompetitionId(), request.getStatus());
        registrations.sort(java.util.Comparator.comparing(Registration::getId));
        int groupSize = request.getGroupSize();
        int groupIndex = 1;
        int counter = 0;
        for (Registration registration : registrations) {
            if (counter >= groupSize) {
                groupIndex += 1;
                counter = 0;
            }
            registration.setGroupCode(request.getGroupPrefix() + groupIndex);
            counter += 1;
        }
        return registrationRepository.saveAll(registrations);
    }

    @Transactional(readOnly = true)
    public List<GroupedRegistrationResponse> groupByGroupCode(Long competitionId) {
        List<Registration> registrations = registrationRepository.findByCompetitionIdWithInstitution(competitionId);
        Map<String, List<Registration>> grouped = new LinkedHashMap<>();
        for (Registration registration : registrations) {
            // 只处理已提交状态的报名
            if (registration.getStatus() != com.trae.pinguan.domain.enums.RegistrationStatus.SUBMITTED) {
                continue;
            }
            String key = registration.getGroupCode() == null || registration.getGroupCode().trim().isEmpty()
                    ? registration.getGroupType().name()
                    : registration.getGroupCode();
            grouped.computeIfAbsent(key, value -> new ArrayList<>()).add(registration);
        }
        List<GroupedRegistrationResponse> responses = new ArrayList<>();
        for (Map.Entry<String, List<Registration>> entry : grouped.entrySet()) {
            List<GroupedRegistrationItem> items = entry.getValue().stream()
                    .map(reg -> new GroupedRegistrationItem(
                            reg.getId(),
                            reg.getProjectName(),
                            reg.getInstitution().getName(),
                            reg.getInstitution().getLevel(),
                            reg.getGroupType(),
                            reg.getGroupCode(),
                            reg.getSubmittedAt()
                    ))
                    .collect(Collectors.toList());
            responses.add(new GroupedRegistrationResponse(entry.getKey(), items));
        }
        return responses;
    }
    
    /**
     * 根据code获取label，如果找不到则返回code本身
     */
    private String getLabel(String code) {
        if (code == null || code.trim().isEmpty()) {
            return "未知";
        }
        return dictionaryItemRepository.findByCode(code)
                .map(item -> item.getLabel())
                .orElse(code);
    }
}
