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
import com.trae.pinguan.repository.DictionaryItemRepository;
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
import java.util.HashSet;
import java.util.Set;
import com.trae.pinguan.web.dto.RegistrationCreateRequest;
import com.trae.pinguan.web.dto.RegistrationDetailResponse;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class RegistrationService {
    private final RegistrationRepository registrationRepository;
    private final RegistrationMemberRepository memberRepository;
    private final CompetitionRepository competitionRepository;
    private final InstitutionRepository institutionRepository;
    private final UserAccountRepository userAccountRepository;
    private final ActivityInfoRepository activityInfoRepository;
    private final DictionaryItemRepository dictionaryItemRepository;
    private final ProjectSummaryRepository summaryRepository;
    private final MaterialFileRepository materialRepository;
    private final ReviewTaskRepository reviewTaskRepository;

    @Transactional
    public Registration create(RegistrationCreateRequest request) {
        Competition competition = competitionRepository.findById(request.getCompetitionId())
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        Institution institution = institutionRepository.findById(request.getInstitutionId())
                .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
        UserAccount applicant = userAccountRepository.findById(request.getApplicantId())
                .orElseThrow(() -> new IllegalArgumentException("报名人不存在"));
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
            if (activity.getMethodCode() != null && !activity.getMethodCode().trim().isEmpty()) {
                methodLabel = dictionaryItemRepository
                        .findFirstByTypeAndCodeAndActiveTrue("method", activity.getMethodCode())
                        .map(item -> item.getLabel())
                        .orElse(null);
            }
            if (activity.getSubjectTypeCode() != null && !activity.getSubjectTypeCode().trim().isEmpty()) {
                subjectTypeLabel = dictionaryItemRepository
                        .findFirstByTypeAndCodeAndActiveTrue("subject_type", activity.getSubjectTypeCode())
                        .map(item -> item.getLabel())
                        .orElse(null);
            }
            activityDetail = new ActivityInfoDetailResponse(
                    activity.getTheme(),
                    activity.getKeywords(),
                    activity.getSubjectTypeCode(),
                    activity.getSubjectTypeOther(),
                    subjectTypeLabel,
                    activity.getMethodCode(),
                    activity.getMethodOther(),
                    activity.getExperienceImproveCode(),
                    activity.getExperienceImproveOther(),
                    activity.getQualityTopicCode(),
                    activity.getQualityTopicOther(),
                    activity.getAvgWorkYears(),
                    activity.getAvgAge(),
                    activity.getCrossDepartment(),
                    methodLabel
            );
        }
        return new RegistrationDetailResponse(registration, institutionInfo, members, activityDetail, summary, materials);
    }

    public List<Registration> listByCompetition(Long competitionId) {
        return registrationRepository.findByCompetitionId(competitionId);
    }

    public List<Registration> listByCompetitionAndStatus(Long competitionId, RegistrationStatus status) {
        return registrationRepository.findByCompetitionIdAndStatus(competitionId, status);
    }

    @Transactional(readOnly = true)
    public List<com.trae.pinguan.web.dto.MyRegistrationItem> listByApplicant(Long applicantId) {
        List<Registration> registrations = registrationRepository.findByApplicantId(applicantId);
        return registrations.stream()
                .map(reg -> com.trae.pinguan.web.dto.MyRegistrationItem.builder()
                        .id(reg.getId())
                        .competitionId(reg.getCompetitionId())
                        .institutionId(reg.getInstitutionId())
                        .institutionName(reg.getInstitution() != null ? reg.getInstitution().getName() : null)
                        .institutionLevel(reg.getInstitution() != null ? reg.getInstitution().getLevel() : null)
                        .applicantId(reg.getApplicantId())
                        .projectName(reg.getProjectName())
                        .groupType(reg.getGroupType())
                        .groupCode(reg.getGroupCode())
                        .status(reg.getStatus())
                        .submittedAt(reg.getSubmittedAt())
                        .createdAt(reg.getCreatedAt())
                        .build())
                .collect(java.util.stream.Collectors.toList());
    }

    public List<Registration> listByInstitution(Long institutionId) {
        return registrationRepository.findByInstitutionId(institutionId);
    }

    /**
     * 查询报名筛选列表（支持分页）
     * 
     * @param page 页码（从1开始），null表示不分页
     * @param size 每页数量，默认20
     * @return 不分页时返回List，分页时返回PageResult
     */
    public Object filterRegistrations(Long competitionId,
                                     com.trae.pinguan.domain.enums.GroupType groupType,
                                     String groupCode,
                                     String projectName,
                                     String institutionName,
                                     String methodCode,
                                     String methodLabel,
                                     String subjectTypeCode,
                                     String subjectTypeLabel,
                                     Integer page,
                                     Integer size) {
        // 如果不分页，使用原有逻辑
        if (page == null) {
            return filterRegistrationsWithoutPagination(competitionId, groupType, groupCode, projectName,
                    institutionName, methodCode, methodLabel, subjectTypeCode, subjectTypeLabel);
        }
        
        // 分页查询
        return filterRegistrationsWithPagination(competitionId, groupType, groupCode, projectName,
                institutionName, methodCode, methodLabel, subjectTypeCode, subjectTypeLabel, page, size);
    }
    
    /**
     * 不分页查询（保留原有逻辑）
     */
    private List<RegistrationFilterItem> filterRegistrationsWithoutPagination(Long competitionId,
                                                            com.trae.pinguan.domain.enums.GroupType groupType,
                                                            String groupCode,
                                                            String projectName,
                                                            String institutionName,
                                                            String methodCode,
                                                            String methodLabel,
                                                            String subjectTypeCode,
                                                            String subjectTypeLabel) {
        String groupCodeValue = groupCode == null || groupCode.trim().isEmpty() ? null : groupCode.trim();
        String projectNameValue = projectName == null || projectName.trim().isEmpty() ? null : projectName.trim();
        String institutionNameValue = institutionName == null || institutionName.trim().isEmpty() ? null : institutionName.trim();
        
        // 如果传了methodLabel，转换为methodCode（支持多个匹配）
        String methodCodeValue = methodCode;
        List<String> methodCodes = null;
        if ((methodCodeValue == null || methodCodeValue.trim().isEmpty()) && methodLabel != null && !methodLabel.trim().isEmpty()) {
            // 根据label查找所有匹配的code（可能有多个）
            methodCodes = dictionaryItemRepository.findByTypeAndActiveOrderByIdAsc("method", true)
                    .stream()
                    .filter(item -> methodLabel.trim().equals(item.getLabel()))
                    .map(item -> item.getCode())
                    .collect(Collectors.toList());
        }
        methodCodeValue = methodCodeValue == null || methodCodeValue.trim().isEmpty() ? null : methodCodeValue.trim();
        
        // 如果传了subjectTypeLabel，转换为subjectTypeCode（支持多个匹配）
        String subjectTypeCodeValue = subjectTypeCode;
        List<String> subjectTypeCodes = null;
        if ((subjectTypeCodeValue == null || subjectTypeCodeValue.trim().isEmpty()) && subjectTypeLabel != null && !subjectTypeLabel.trim().isEmpty()) {
            // 根据label查找所有匹配的code（可能有多个）
            subjectTypeCodes = dictionaryItemRepository.findByTypeAndActiveOrderByIdAsc("subject_type", true)
                    .stream()
                    .filter(item -> subjectTypeLabel.trim().equals(item.getLabel()))
                    .map(item -> item.getCode())
                    .collect(Collectors.toList());
        }
        subjectTypeCodeValue = subjectTypeCodeValue == null || subjectTypeCodeValue.trim().isEmpty() ? null : subjectTypeCodeValue.trim();
        
        // 如果methodLabel匹配了多个code，需要分别查询然后合并结果
        List<RegistrationFilterItem> items;
        if (methodCodeValue == null && methodCodes != null && methodCodes.size() > 1) {
            // 多个methodCode匹配，分别查询
            items = new ArrayList<>();
            Set<Long> seenIds = new HashSet<>();
            for (String code : methodCodes) {
                List<RegistrationFilterItem> partialItems = registrationRepository.filterRegistrations(
                        competitionId,
                        groupType,
                        groupCodeValue,
                        projectNameValue,
                        institutionNameValue,
                        code,
                        subjectTypeCodeValue
                );
                // 去重
                for (RegistrationFilterItem item : partialItems) {
                    if (!seenIds.contains(item.getRegistrationId())) {
                        items.add(item);
                        seenIds.add(item.getRegistrationId());
                    }
                }
            }
        } else if (subjectTypeCodeValue == null && subjectTypeCodes != null && subjectTypeCodes.size() > 1) {
            // 多个subjectTypeCode匹配，分别查询
            items = new ArrayList<>();
            Set<Long> seenIds = new HashSet<>();
            for (String code : subjectTypeCodes) {
                List<RegistrationFilterItem> partialItems = registrationRepository.filterRegistrations(
                        competitionId,
                        groupType,
                        groupCodeValue,
                        projectNameValue,
                        institutionNameValue,
                        methodCodeValue,
                        code
                );
                // 去重
                for (RegistrationFilterItem item : partialItems) {
                    if (!seenIds.contains(item.getRegistrationId())) {
                        items.add(item);
                        seenIds.add(item.getRegistrationId());
                    }
                }
            }
        } else {
            // 单个code或没有label，正常查询
            if (methodCodeValue == null && methodCodes != null && methodCodes.size() == 1) {
                methodCodeValue = methodCodes.get(0);
            }
            if (subjectTypeCodeValue == null && subjectTypeCodes != null && subjectTypeCodes.size() == 1) {
                subjectTypeCodeValue = subjectTypeCodes.get(0);
            }
            items = registrationRepository.filterRegistrations(
                    competitionId,
                    groupType,
                    groupCodeValue,
                    projectNameValue,
                    institutionNameValue,
                    methodCodeValue,
                    subjectTypeCodeValue
            );
        }
        
        if (items.isEmpty()) {
            return items;
        }
        Map<String, String> methodLabels = dictionaryItemRepository.findByTypeAndActiveOrderByIdAsc("method", true)
                .stream()
                .collect(Collectors.toMap(item -> item.getCode(), item -> item.getLabel(), (a, b) -> a));
        Map<String, String> subjectTypeLabels = dictionaryItemRepository.findByTypeAndActiveOrderByIdAsc("subject_type", true)
                .stream()
                .collect(Collectors.toMap(item -> item.getCode(), item -> item.getLabel(), (a, b) -> a));
        for (RegistrationFilterItem item : items) {
            if (item.getMethodCode() != null) {
                item.setMethodLabel(methodLabels.get(item.getMethodCode()));
            }
            if (item.getSubjectTypeCode() != null) {
                item.setSubjectTypeLabel(subjectTypeLabels.get(item.getSubjectTypeCode()));
            }
        }
        return items;
    }
    
    /**
     * 分页查询（页码从1开始）
     */
    private com.trae.pinguan.web.dto.PageResult<RegistrationFilterItem> filterRegistrationsWithPagination(
            Long competitionId,
            com.trae.pinguan.domain.enums.GroupType groupType,
            String groupCode,
            String projectName,
            String institutionName,
            String methodCode,
            String methodLabel,
            String subjectTypeCode,
            String subjectTypeLabel,
            Integer page,
            Integer size) {
        
        // 参数处理
        int actualPage = page != null && page > 0 ? page : 1;  // 确保page至少为1
        int pageNumber = actualPage - 1;  // 转换：1-based -> 0-based
        int pageSize = size != null && size > 0 ? size : 20;  // 默认20条/页
        
        // 创建分页对象
        org.springframework.data.domain.Pageable pageable = org.springframework.data.domain.PageRequest.of(
                pageNumber, pageSize,
                org.springframework.data.domain.Sort.by(org.springframework.data.domain.Sort.Direction.DESC, "submittedAt")
        );
        
        String groupCodeValue = groupCode == null || groupCode.trim().isEmpty() ? null : groupCode.trim();
        String projectNameValue = projectName == null || projectName.trim().isEmpty() ? null : projectName.trim();
        String institutionNameValue = institutionName == null || institutionName.trim().isEmpty() ? null : institutionName.trim();
        
        // 处理 methodLabel 转换
        String methodCodeValue = methodCode;
        if ((methodCodeValue == null || methodCodeValue.trim().isEmpty()) && methodLabel != null && !methodLabel.trim().isEmpty()) {
            methodCodeValue = dictionaryItemRepository.findByTypeAndActiveOrderByIdAsc("method", true)
                    .stream()
                    .filter(item -> methodLabel.trim().equals(item.getLabel()))
                    .map(item -> item.getCode())
                    .findFirst()
                    .orElse(null);
        }
        methodCodeValue = methodCodeValue == null || methodCodeValue.trim().isEmpty() ? null : methodCodeValue.trim();
        
        // 处理 subjectTypeLabel 转换
        String subjectTypeCodeValue = subjectTypeCode;
        if ((subjectTypeCodeValue == null || subjectTypeCodeValue.trim().isEmpty()) && subjectTypeLabel != null && !subjectTypeLabel.trim().isEmpty()) {
            subjectTypeCodeValue = dictionaryItemRepository.findByTypeAndActiveOrderByIdAsc("subject_type", true)
                    .stream()
                    .filter(item -> subjectTypeLabel.trim().equals(item.getLabel()))
                    .map(item -> item.getCode())
                    .findFirst()
                    .orElse(null);
        }
        subjectTypeCodeValue = subjectTypeCodeValue == null || subjectTypeCodeValue.trim().isEmpty() ? null : subjectTypeCodeValue.trim();
        
        // 分页查询
        org.springframework.data.domain.Page<RegistrationFilterItem> itemPage = registrationRepository.filterRegistrationsPaged(
                competitionId,
                groupType,
                groupCodeValue,
                projectNameValue,
                institutionNameValue,
                methodCodeValue,
                subjectTypeCodeValue,
                pageable
        );
        
        // 如果无数据，返回空分页结果
        if (itemPage.isEmpty()) {
            return com.trae.pinguan.web.dto.PageResult.<RegistrationFilterItem>builder()
                    .content(new ArrayList<>())
                    .pageNo(actualPage)
                    .pageSize(pageSize)
                    .totalCount(0L)
                    .totalPages(0)
                    .hasNext(false)
                    .hasPrevious(false)
                    .build();
        }
        
        // 填充label
        List<RegistrationFilterItem> items = itemPage.getContent();
        Map<String, String> methodLabels = dictionaryItemRepository.findByTypeAndActiveOrderByIdAsc("method", true)
                .stream()
                .collect(Collectors.toMap(item -> item.getCode(), item -> item.getLabel(), (a, b) -> a));
        Map<String, String> subjectTypeLabels = dictionaryItemRepository.findByTypeAndActiveOrderByIdAsc("subject_type", true)
                .stream()
                .collect(Collectors.toMap(item -> item.getCode(), item -> item.getLabel(), (a, b) -> a));
        
        for (RegistrationFilterItem item : items) {
            if (item.getMethodCode() != null) {
                item.setMethodLabel(methodLabels.get(item.getMethodCode()));
            }
            if (item.getSubjectTypeCode() != null) {
                item.setSubjectTypeLabel(subjectTypeLabels.get(item.getSubjectTypeCode()));
            }
        }
        
        // 构造分页结果（页码转换回1-based）
        return com.trae.pinguan.web.dto.PageResult.<RegistrationFilterItem>builder()
                .content(items)
                .pageNo(actualPage)
                .pageSize(pageSize)
                .totalCount(itemPage.getTotalElements())
                .totalPages(itemPage.getTotalPages())
                .hasNext(itemPage.hasNext())
                .hasPrevious(itemPage.hasPrevious())
                .build();
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
                            reg.getGroupType(),
                            reg.getGroupCode()
                    ))
                    .collect(Collectors.toList());
            responses.add(new GroupedRegistrationResponse(entry.getKey(), items));
        }
        return responses;
    }
}
