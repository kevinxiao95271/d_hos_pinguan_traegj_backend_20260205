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
    private final com.trae.pinguan.repository.SystemSettingRepository systemSettingRepository;

    @Transactional
    public Registration create(RegistrationCreateRequest request) {
        Competition competition = competitionRepository.findById(request.getCompetitionId())
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        Institution institution = institutionRepository.findById(request.getInstitutionId())
                .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
        UserAccount applicant = userAccountRepository.findById(request.getApplicantId())
                .orElseThrow(() -> new IllegalArgumentException("报名人不存在"));
        
        // 检查机构报名数量限制
        int maxRegistrationsPerInstitution = systemSettingRepository
                .findBySettingKey("maxRegistrationsPerInstitution")
                .map(setting -> Integer.parseInt(setting.getSettingValue()))
                .orElse(8);  // 默认值为8
        
        long currentCount = registrationRepository
                .findByCompetitionIdAndInstitutionId(competition.getId(), institution.getId())
                .size();
        
        if (currentCount >= maxRegistrationsPerInstitution) {
            throw new IllegalArgumentException(
                    String.format("该机构报名数量已达上限（%d个项目），无法继续报名", maxRegistrationsPerInstitution));
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
            if (activity.getExperienceImproveCode() != null && !activity.getExperienceImproveCode().trim().isEmpty()) {
                experienceImproveLabel = dictionaryItemRepository
                        .findFirstByTypeAndCodeAndActiveTrue("experience_improve", activity.getExperienceImproveCode())
                        .map(item -> item.getLabel())
                        .orElse(null);
            }
            if (activity.getQualityTopicCode() != null && !activity.getQualityTopicCode().trim().isEmpty()) {
                qualityTopicLabel = dictionaryItemRepository
                        .findFirstByTypeAndCodeAndActiveTrue("quality_topic", activity.getQualityTopicCode())
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
        return new RegistrationDetailResponse(registration, institutionInfo, members, activityDetail, summary, materials);
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

    @Transactional(readOnly = true)
    public com.trae.pinguan.web.dto.InstitutionQuotaResponse getInstitutionQuota(Long competitionId, Long institutionId) {
        Competition competition = competitionRepository.findById(competitionId)
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        Institution institution = institutionRepository.findById(institutionId)
                .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
        
        // 获取最大报名数量限制
        int maxCount = systemSettingRepository
                .findBySettingKey("maxRegistrationsPerInstitution")
                .map(setting -> Integer.parseInt(setting.getSettingValue()))
                .orElse(8);  // 默认值为8
        
        // 统计当前已报名数量
        int currentCount = registrationRepository
                .findByCompetitionIdAndInstitutionId(competitionId, institutionId)
                .size();
        
        // 计算剩余可报名数量
        int remainingCount = Math.max(0, maxCount - currentCount);
        
        // 判断是否还可以报名
        boolean canRegister = currentCount < maxCount;
        
        return com.trae.pinguan.web.dto.InstitutionQuotaResponse.builder()
                .institutionId(institutionId)
                .institutionName(institution.getName())
                .competitionId(competitionId)
                .competitionName(competition.getName())
                .currentCount(currentCount)
                .maxCount(maxCount)
                .remainingCount(remainingCount)
                .canRegister(canRegister)
                .build();
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
        // 获取所有待分组的报名
        List<Registration> registrations = request.getStatus() == null
                ? registrationRepository.findByCompetitionId(request.getCompetitionId())
                : registrationRepository.findByCompetitionIdAndStatus(request.getCompetitionId(), request.getStatus());
        
        if (registrations.isEmpty()) {
            return registrations;
        }
        
        // 按groupType分组处理（基层组/综合组/进阶组）
        Map<com.trae.pinguan.domain.enums.GroupType, List<Registration>> byGroupType = registrations.stream()
                .collect(Collectors.groupingBy(Registration::getGroupType));
        
        // 对每个groupType独立分组
        for (Map.Entry<com.trae.pinguan.domain.enums.GroupType, List<Registration>> entry : byGroupType.entrySet()) {
            com.trae.pinguan.domain.enums.GroupType groupType = entry.getKey();
            List<Registration> typeRegistrations = entry.getValue();
            
            // 确定分组前缀（A=基层组, B=综合组, C=进阶组）
            String prefix = getGroupPrefix(groupType);
            
            // 执行智能分组
            assignGroupCodes(typeRegistrations, prefix, request);
        }
        
        return registrationRepository.saveAll(registrations);
    }
    
    private String getGroupPrefix(com.trae.pinguan.domain.enums.GroupType groupType) {
        switch (groupType) {
            case BASIC:
                return "A";
            case COMPREHENSIVE:
                return "B";
            case ADVANCED:
                return "C";
            default:
                return "X";
        }
    }
    
    private void assignGroupCodes(List<Registration> registrations, String prefix, AutoGroupRequest request) {
        int totalProjects = registrations.size();
        int minSize = request.getMinGroupSize();
        int maxSize = request.getMaxGroupSize();
        int maxSpread = request.getMaxInstitutionSpread();
        
        // 计算最优分组数量
        int numGroups = calculateOptimalGroupCount(totalProjects, minSize, maxSize);
        
        // 按机构分组统计
        Map<Long, List<Registration>> byInstitution = registrations.stream()
                .collect(Collectors.groupingBy(reg -> reg.getInstitution().getId()));
        
        // 创建分组桶
        List<List<Registration>> buckets = new ArrayList<>();
        for (int i = 0; i < numGroups; i++) {
            buckets.add(new ArrayList<>());
        }
        
        // 按机构项目数降序排序（大机构优先分配）
        List<Map.Entry<Long, List<Registration>>> institutionEntries = new ArrayList<>(byInstitution.entrySet());
        institutionEntries.sort((a, b) -> Integer.compare(b.getValue().size(), a.getValue().size()));
        
        // 分配策略：同机构项目尽量集中在1-2个分组
        for (Map.Entry<Long, List<Registration>> entry : institutionEntries) {
            List<Registration> instProjects = entry.getValue();
            int projectCount = instProjects.size();
            
            // 确定该机构需要占用的分组数
            int groupsNeeded = Math.min(
                    (projectCount + maxSize - 1) / maxSize,  // 基于容量计算
                    Math.min(maxSpread, (projectCount + minSize - 1) / minSize)  // 基于散落限制
            );
            groupsNeeded = Math.max(1, Math.min(groupsNeeded, numGroups));
            
            // 找到当前最空的N个桶
            List<Integer> targetBuckets = findLeastLoadedBuckets(buckets, groupsNeeded);
            
            // 将项目分配到这些桶中
            int projectsPerBucket = projectCount / groupsNeeded;
            int remainder = projectCount % groupsNeeded;
            
            int projectIndex = 0;
            for (int i = 0; i < groupsNeeded; i++) {
                int bucketIndex = targetBuckets.get(i);
                int count = projectsPerBucket + (i < remainder ? 1 : 0);
                
                for (int j = 0; j < count && projectIndex < projectCount; j++) {
                    buckets.get(bucketIndex).add(instProjects.get(projectIndex++));
                }
            }
        }
        
        // 分配group_code
        for (int i = 0; i < buckets.size(); i++) {
            String groupCode = prefix + (i + 1);
            for (Registration reg : buckets.get(i)) {
                reg.setGroupCode(groupCode);
            }
        }
    }
    
    private int calculateOptimalGroupCount(int totalProjects, int minSize, int maxSize) {
        // 目标：让每组项目数在minSize和maxSize之间，且尽量均衡
        int targetSize = (minSize + maxSize) / 2;  // 目标大小约25-26
        int numGroups = (totalProjects + targetSize - 1) / targetSize;
        
        // 确保不会超出范围
        int minGroups = (totalProjects + maxSize - 1) / maxSize;
        int maxGroups = (totalProjects + minSize - 1) / minSize;
        
        numGroups = Math.max(minGroups, Math.min(numGroups, maxGroups));
        
        return Math.max(1, numGroups);
    }
    
    private List<Integer> findLeastLoadedBuckets(List<List<Registration>> buckets, int count) {
        // 找到当前负载最小的N个桶
        List<Integer> indices = new ArrayList<>();
        for (int i = 0; i < buckets.size(); i++) {
            indices.add(i);
        }
        
        indices.sort(java.util.Comparator.comparingInt(i -> buckets.get(i).size()));
        
        return indices.subList(0, Math.min(count, indices.size()));
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
                            reg.getInstitution().getLevel(),
                            reg.getGroupType(),
                            reg.getGroupCode()
                    ))
                    .collect(Collectors.toList());
            responses.add(new GroupedRegistrationResponse(entry.getKey(), items));
        }
        return responses;
    }
}
