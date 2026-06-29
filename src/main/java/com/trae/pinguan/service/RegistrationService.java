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
import com.trae.pinguan.repository.ReviewScoreRepository;
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
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
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
    private final ReviewScoreRepository reviewScoreRepository;
    private final FileStorageService fileStorageService;
    private static final String PAYMENT_PROOF_TYPE = "payment_proof";
    private static final String REGISTRATION_FORM_DOC_TYPE = "REGISTRATION_FORM_DOC";
    private static final String REGISTRATION_FORM_PDF_TYPE = "REGISTRATION_FORM_PDF";

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

        validateBasicGroupEligibility(institution, request.getGroupType());
        
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
        if (request.getProjectLeaderName() != null) {
            registration.setProjectLeaderName(request.getProjectLeaderName());
        }
        if (request.getProjectLeaderPhone() != null) {
            registration.setProjectLeaderPhone(request.getProjectLeaderPhone());
        }
        if (request.getProjectLeaderTitle() != null) {
            registration.setProjectLeaderTitle(request.getProjectLeaderTitle());
        }

        validateBasicGroupEligibility(registration.getInstitution(), registration.getGroupType());
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
        // 服务端相似度拦截：与同机构已提交记录对比，≥80% 直接拒绝（先于材料检查，让用户优先处理名称冲突）
        if (registration.getInstitution() != null && registration.getProjectName() != null) {
            Long compId = registration.getCompetition().getId();
            Long instId = registration.getInstitution().getId();
            List<Map<String, Object>> hits = checkDuplicate(compId, instId,
                    registration.getProjectName(), registrationId);
            List<Map<String, Object>> blocked = hits.stream()
                    .filter(h -> ((Number) h.get("similarity")).doubleValue() >= 80.0)
                    .collect(Collectors.toList());
            if (!blocked.isEmpty()) {
                throw new com.trae.pinguan.exception.DuplicateProjectNameException(blocked);
            }
        }

        validateRequiredMaterialsBeforeSubmit(registrationId);

        // 首次提交时生成项目编号（退回后再次提交不重新生成）
        if (registration.getRegistrationCode() == null) {
            Long competitionId = registration.getCompetition().getId();
            int nextCode = registrationRepository
                    .findMaxRegistrationCodeByCompetitionId(competitionId)
                    .map(max -> max + 1)
                    .orElse(1);
            registration.setRegistrationCode(nextCode);
        }
        registration.setStatus(RegistrationStatus.SUBMITTED);
        registration.setSubmittedAt(LocalDateTime.now());
        return registrationRepository.save(registration);
    }

    @Transactional
    public Registration returnForEdit(Long registrationId) {
        Registration registration = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        boolean scored = reviewTaskRepository.findByRegistrationId(registrationId).stream()
                .anyMatch(task -> task.getStatus() == com.trae.pinguan.domain.enums.ReviewStatus.SCORED);
        if (scored) {
            throw new IllegalArgumentException("已评分无法退回");
        }
        registration.setStatus(RegistrationStatus.RETURNED);
        return registrationRepository.save(registration);
    }

    @Transactional(readOnly = true)
    public long countByInstitution(Long competitionId, Long applicantId) {
        UserAccount user = userAccountRepository.findById(applicantId)
                .orElseThrow(() -> new IllegalArgumentException("用户不存在"));
        if (user.getInstitution() == null) {
            return 0L;
        }
        return registrationRepository.countActiveByCompetitionAndInstitution(
                competitionId, user.getInstitution().getId());
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
        List<MaterialFile> allMaterials = materialRepository.findByRegistrationId(registrationId);
        List<MaterialFile> paymentProofs = allMaterials.stream()
                .filter(m -> PAYMENT_PROOF_TYPE.equalsIgnoreCase(m.getType()))
                .collect(Collectors.toList());
        List<MaterialFile> materials = allMaterials.stream()
                .filter(m -> !PAYMENT_PROOF_TYPE.equalsIgnoreCase(m.getType()))
                .collect(Collectors.toList());
        ActivityInfoDetailResponse activityDetail = null;
        if (activity != null) {
            String methodLabel = null;
            String subjectTypeLabel = null;
            String experienceImproveLabel = null;
            String qualityTopicLabel = null;
            
            // 从字典表查询label
            if (activity.getMethodCode() != null && !activity.getMethodCode().trim().isEmpty()) {
                methodLabel = getLabel(activity.getMethodCode());
            }
            if (activity.getSubjectTypeCode() != null && !activity.getSubjectTypeCode().trim().isEmpty()) {
                subjectTypeLabel = getLabel(activity.getSubjectTypeCode());
            }
            if (activity.getExperienceImproveCode() != null && !activity.getExperienceImproveCode().trim().isEmpty()) {
                experienceImproveLabel = getLabel(activity.getExperienceImproveCode());
            }
            if (activity.getQualityTopicCode() != null && !activity.getQualityTopicCode().trim().isEmpty()) {
                qualityTopicLabel = getLabel(activity.getQualityTopicCode());
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
                .paymentProofs(paymentProofs)
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

    public Page<RegistrationFilterItem> filterRegistrations(Long competitionId,
                                                            com.trae.pinguan.domain.enums.RegistrationStatus status,
                                                            com.trae.pinguan.domain.enums.GroupType groupType,
                                                            String groupCode,
                                                            Integer registrationCode,
                                                            String projectName,
                                                            String institutionName,
                                                            String methodCode,
                                                            String subjectTypeCode,
                                                            Boolean hasPaymentProof,
                                                            int page,
                                                            int size) {
        String groupCodeValue = groupCode == null || groupCode.trim().isEmpty() ? null : groupCode.trim();
        String projectNameValue = projectName == null || projectName.trim().isEmpty() ? null : projectName.trim();
        String institutionNameValue = institutionName == null || institutionName.trim().isEmpty() ? null : institutionName.trim();
        String methodCodeValue = methodCode == null || methodCode.trim().isEmpty() ? null : methodCode.trim();
        String subjectTypeCodeValue = subjectTypeCode == null || subjectTypeCode.trim().isEmpty() ? null : subjectTypeCode.trim();
        // page 参数从1开始，转为0-based传给JPA
        PageRequest pageable = PageRequest.of(Math.max(0, page - 1), size, Sort.by(Sort.Direction.ASC, "id"));
        Page<RegistrationFilterItem> pageResult = registrationRepository.filterRegistrations(
                competitionId,
                status,
                groupType,
                groupCodeValue,
                registrationCode,
                projectNameValue,
                institutionNameValue,
                methodCodeValue,
                subjectTypeCodeValue,
                hasPaymentProof,
                pageable
        );
        List<RegistrationFilterItem> items = pageResult.getContent();
        if (items.isEmpty()) {
            return pageResult;
        }

        // 批量查询字典label（1次DB，替代原来每条N次）
        java.util.Set<String> codes = new java.util.HashSet<>();
        for (RegistrationFilterItem item : items) {
            if (item.getMethodCode() != null) codes.add(item.getMethodCode());
            if (item.getSubjectTypeCode() != null) codes.add(item.getSubjectTypeCode());
        }
        Map<String, String> labelMap = new java.util.HashMap<>();
        if (!codes.isEmpty()) {
            dictionaryItemRepository.findByCodes(codes)
                    .forEach(d -> labelMap.putIfAbsent(d.getCode(), d.getLabel()));
        }
        for (RegistrationFilterItem item : items) {
            if (item.getMethodCode() != null) {
                item.setMethodLabel(labelMap.getOrDefault(item.getMethodCode(), item.getMethodCode()));
            }
            if (item.getSubjectTypeCode() != null) {
                item.setSubjectTypeLabel(labelMap.getOrDefault(item.getSubjectTypeCode(), item.getSubjectTypeCode()));
            }
        }

        // 批量查询材料文件
        List<Long> registrationIds = items.stream()
                .map(RegistrationFilterItem::getRegistrationId)
                .collect(Collectors.toList());

        if (!registrationIds.isEmpty()) {
            // 查询所有材料文件并按 registration_id 分组（用registrationId避免触发懒加载）
            Map<Long, List<MaterialFile>> materialsMap = materialRepository
                    .findByRegistrationIdIn(registrationIds)
                    .stream()
                    .collect(Collectors.groupingBy((MaterialFile m) -> m.getRegistrationId()));

            // 组装材料文件到每个 item
            for (RegistrationFilterItem item : items) {
                List<MaterialFile> materials = materialsMap.getOrDefault(
                        item.getRegistrationId(), new ArrayList<>()
                );

                List<RegistrationFilterItem.MaterialFileSimple> materialSimples = materials.stream()
                        .map(m -> new RegistrationFilterItem.MaterialFileSimple(
                                m.getId(),
                                m.getType(),
                                m.getFileName(),
                                "/api/materials/" + m.getId() + "/download",
                                m.getUploadedAt()
                        ))
                        .collect(Collectors.toList());

                List<RegistrationFilterItem.MaterialFileSimple> paymentProofs = materialSimples.stream()
                        .filter(m -> PAYMENT_PROOF_TYPE.equalsIgnoreCase(m.getType()))
                        .collect(Collectors.toList());
                List<RegistrationFilterItem.MaterialFileSimple> normalMaterials = materialSimples.stream()
                        .filter(m -> !PAYMENT_PROOF_TYPE.equalsIgnoreCase(m.getType()))
                        .collect(Collectors.toList());

                item.setMaterials(normalMaterials);
                item.setPaymentProofs(paymentProofs);
            }
        }

        return pageResult;
    }

    @Transactional
    public List<Registration> batchClassify(BatchClassificationRequest request) {
        List<Registration> registrations = registrationRepository.findAllById(request.getRegistrationIds());
        if (registrations.isEmpty()) return registrations;
        Competition competition = registrations.get(0).getCompetition();
        String newGroupCode = request.getGroupCode();
        for (Registration registration : registrations) {
            String expectedPrefix = groupTypeToPrefix(registration.getGroupType(), competition);
            if (!newGroupCode.startsWith(expectedPrefix)) {
                throw new IllegalArgumentException(
                        "项目 [" + registration.getProjectName() + "] 属于" +
                        groupTypeLabel(registration.getGroupType()) +
                        ", groupCode must start with '" + expectedPrefix + "', but got: " + newGroupCode);
            }
        }
        for (Registration registration : registrations) {
            registration.setGroupCode(newGroupCode);
        }
        return registrationRepository.saveAll(registrations);
    }

    private String groupTypeToPrefix(com.trae.pinguan.domain.enums.GroupType groupType, Competition competition) {
        if (groupType == null) return "";
        switch (groupType) {
            case BASIC:
                return competition.getBasicGroupPrefix() != null ? competition.getBasicGroupPrefix().toUpperCase() : "A";
            case COMPREHENSIVE:
                return competition.getComprehensiveGroupPrefix() != null ? competition.getComprehensiveGroupPrefix().toUpperCase() : "B";
            case ADVANCED:
                return competition.getAdvancedGroupPrefix() != null ? competition.getAdvancedGroupPrefix().toUpperCase() : "C";
            default: return "";
        }
    }

    private java.util.Set<String> validPrefixes(Competition competition) {
        return new java.util.HashSet<>(java.util.Arrays.asList(
            competition.getBasicGroupPrefix()         != null ? competition.getBasicGroupPrefix().toUpperCase()         : "A",
            competition.getComprehensiveGroupPrefix() != null ? competition.getComprehensiveGroupPrefix().toUpperCase() : "B",
            competition.getAdvancedGroupPrefix()      != null ? competition.getAdvancedGroupPrefix().toUpperCase()      : "C"
        ));
    }

    private String groupTypeLabel(com.trae.pinguan.domain.enums.GroupType groupType) {
        if (groupType == null) return "未知组";
        switch (groupType) {
            case BASIC:         return "基层组";
            case COMPREHENSIVE: return "综合组";
            case ADVANCED:      return "进阶组";
            default:            return groupType.name();
        }
    }

    @Transactional
    public List<Registration> autoGroup(AutoGroupRequest request) {
        Competition competition = competitionRepository.findById(request.getCompetitionId())
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在: " + request.getCompetitionId()));

        // ── 前缀校验与推导 ──────────────────────────────────────────────────────
        String resolvedPrefix;
        if (request.getGroupPrefix() != null) {
            String p = request.getGroupPrefix().trim().toUpperCase();
            if (request.getGroupType() != null) {
                String expected = groupTypeToPrefix(request.getGroupType(), competition);
                if (!p.equals(expected)) {
                    throw new IllegalArgumentException(
                            "groupPrefix '" + p + "' 与 groupType " + groupTypeLabel(request.getGroupType())
                            + " 不匹配，该赛事配置应为 '" + expected + "'");
                }
            } else if (!validPrefixes(competition).contains(p)) {
                throw new IllegalArgumentException(
                        "groupPrefix 非法：'" + p + "'，该赛事有效前缀为 " + validPrefixes(competition));
            }
            resolvedPrefix = p;
        } else {
            if (request.getGroupType() == null) {
                throw new IllegalArgumentException(
                        "groupType 与 groupPrefix 不能同时为空，请至少指定其中一个");
            }
            resolvedPrefix = groupTypeToPrefix(request.getGroupType(), competition);
        }

        // ── 查询报名记录 ────────────────────────────────────────────────────────
        List<Registration> registrations = request.getStatus() == null
                ? registrationRepository.findByCompetitionId(request.getCompetitionId())
                : registrationRepository.findByCompetitionIdAndStatus(request.getCompetitionId(), request.getStatus());

        if (request.getGroupType() != null) {
            registrations = registrations.stream()
                    .filter(r -> r.getGroupType() == request.getGroupType())
                    .collect(java.util.stream.Collectors.toList());
        }

        // ── 分组编号 ────────────────────────────────────────────────────────────
        registrations.sort(java.util.Comparator.comparing(Registration::getId));
        int groupSize = request.getGroupSize();
        int groupIndex = 1;
        int counter = 0;
        for (Registration registration : registrations) {
            if (counter >= groupSize) {
                groupIndex += 1;
                counter = 0;
            }
            registration.setGroupCode(resolvedPrefix + groupIndex);
            counter += 1;
        }
        return registrationRepository.saveAll(registrations);
    }

    @Transactional(readOnly = true)
    public List<GroupedRegistrationResponse> groupByGroupCode(Long competitionId) {
        return groupByGroupCode(competitionId, null);
    }
    
    public List<GroupedRegistrationResponse> groupByGroupCode(Long competitionId, com.trae.pinguan.domain.enums.GroupType groupType) {
        List<Registration> registrations = registrationRepository.findByCompetitionIdWithInstitution(competitionId);
        Map<String, List<Registration>> grouped = new LinkedHashMap<>();
        for (Registration registration : registrations) {
            // 只处理已提交状态的报名
            if (registration.getStatus() != com.trae.pinguan.domain.enums.RegistrationStatus.SUBMITTED) {
                continue;
            }
            // 如果指定了 groupType，只处理该类型的报名
            if (groupType != null && registration.getGroupType() != groupType) {
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
        return dictionaryItemRepository.findFirstByCode(code)
                .map(item -> item.getLabel())
                .orElse(code);
    }

    private void validateRequiredMaterialsBeforeSubmit(Long registrationId) {
        List<MaterialFile> files = materialRepository.findByRegistrationId(registrationId);
        boolean hasRegFormDoc = files.stream()
                .anyMatch(m -> REGISTRATION_FORM_DOC_TYPE.equalsIgnoreCase(m.getType()));
        boolean hasRegFormPdf = files.stream()
                .anyMatch(m -> REGISTRATION_FORM_PDF_TYPE.equalsIgnoreCase(m.getType()));
        if (!hasRegFormDoc || !hasRegFormPdf) {
            throw new IllegalArgumentException("提交前需同时上传报名表Word和PDF（盖章扫描件）");
        }
    }

    private void validateBasicGroupEligibility(Institution institution, com.trae.pinguan.domain.enums.GroupType groupType) {
        if (institution == null || groupType == null) {
            return;
        }
        if (groupType == com.trae.pinguan.domain.enums.GroupType.BASIC) {
            String level = institution.getLevel() == null ? "" : institution.getLevel().trim();
            if (level.startsWith("三级")) {
                throw new IllegalArgumentException("三级医疗机构不可选择基层组，请选择综合组或进阶组");
            }
        }
    }
    
    /**
     * 修复无效的字典code（临时方法）
     */
    @Transactional
    public String fixInvalidDictionaryCodes() {
        StringBuilder result = new StringBuilder();
        
        // 查找所有activity_info
        List<ActivityInfo> activities = activityInfoRepository.findAll();
        int fixedCount = 0;
        
        for (ActivityInfo activity : activities) {
            boolean needUpdate = false;
            
            // 修复 med_tech -> case_quality
            if ("med_tech".equals(activity.getSubjectTypeCode())) {
                activity.setSubjectTypeCode("case_quality");
                needUpdate = true;
                result.append(String.format("报名ID=%d: subject_type med_tech -> case_quality\n", 
                    activity.getRegistration().getId()));
            }
            
            // 修复 multidisciplinary -> other
            if ("multidisciplinary".equals(activity.getMethodCode())) {
                activity.setMethodCode("other");
                needUpdate = true;
                result.append(String.format("报名ID=%d: method multidisciplinary -> other\n", 
                    activity.getRegistration().getId()));
            }
            
            if (needUpdate) {
                activityInfoRepository.save(activity);
                fixedCount++;
            }
        }
        
        result.insert(0, String.format("修复完成！共处理 %d 条记录\n\n", fixedCount));
        return result.toString();
    }

    /**
     * OPS删除报名及所有关联数据（级联删除）
     */
    @Transactional
    public void deleteRegistration(Long registrationId) {
        if (!registrationRepository.existsById(registrationId)) {
            throw new IllegalArgumentException("报名不存在");
        }

        // 1. 删除评审分数（ReviewScore）
        List<com.trae.pinguan.domain.entity.ReviewTask> tasks = reviewTaskRepository.findByRegistrationId(registrationId);
        for (com.trae.pinguan.domain.entity.ReviewTask task : tasks) {
            reviewScoreRepository.findByReviewTaskId(task.getId()).ifPresent(score -> reviewScoreRepository.delete(score));
        }

        // 2. 删除评审任务（ReviewTask）
        reviewTaskRepository.deleteAll(tasks);

        // 3. 删除材料文件（MaterialFile）及 MinIO 对象
        List<com.trae.pinguan.domain.entity.MaterialFile> files = materialRepository.findByRegistrationId(registrationId);
        for (com.trae.pinguan.domain.entity.MaterialFile file : files) {
            try {
                if (file.getFileUrl() != null) {
                    fileStorageService.delete(file.getFileUrl());
                }
            } catch (Exception e) {
                log.warn("删除MinIO文件失败，忽略继续: {}", file.getFileUrl(), e);
            }
        }
        materialRepository.deleteAll(files);

        // 4. 删除成员（RegistrationMember）
        memberRepository.deleteAll(memberRepository.findByRegistrationId(registrationId));

        // 5. 删除活动信息（ActivityInfo）
        activityInfoRepository.findByRegistrationId(registrationId).ifPresent(activityInfoRepository::delete);

        // 6. 删除项目摘要（ProjectSummary）
        summaryRepository.findByRegistrationId(registrationId).ifPresent(summaryRepository::delete);

        // 7. 删除报名主记录
        registrationRepository.deleteById(registrationId);

        log.info("OPS已删除报名 id={} 及所有关联数据", registrationId);
    }

    // ── 相似项目检测 ──────────────────────────────────────────────────────────

    /**
     * 检测同赛事内同机构是否存在与 projectName 高度相似的已有项目（基于二字组 Jaccard 相似度）。
     *
     * @param competitionId 赛事 ID
     * @param institutionId 申请机构 ID
     * @param projectName   待检测项目名称
     * @param selfId        当前报名 ID（更新时排除自身，创建时传 null）
     * @return 相似度最高的条目列表（相似度 ≥ 0.5 的结果，最多 5 条）
     */
    @Transactional(readOnly = true)
    public List<Map<String, Object>> checkDuplicate(Long competitionId, Long institutionId,
                                                     String projectName, Long selfId) {
        if (projectName == null || projectName.trim().isEmpty()) {
            return new ArrayList<>();
        }
        List<Registration> candidates = registrationRepository.findByCompetitionId(competitionId)
                .stream()
                .filter(r -> r.getInstitution() != null
                        && r.getInstitution().getId().equals(institutionId))
                .filter(r -> selfId == null || !r.getId().equals(selfId))
                .filter(r -> r.getStatus() != RegistrationStatus.DRAFT)
                .collect(Collectors.toList());

        java.util.Set<String> queryBigrams = bigrams(projectName);
        List<Map<String, Object>> results = new ArrayList<>();
        for (Registration r : candidates) {
            java.util.Set<String> targetBigrams = bigrams(r.getProjectName());
            double sim = jaccardSimilarity(queryBigrams, targetBigrams);
            if (sim >= 0.5) {
                Map<String, Object> item = new java.util.LinkedHashMap<>();
                item.put("registrationId", r.getId());
                item.put("projectName", r.getProjectName());
                item.put("status", r.getStatus());
                item.put("similarity", Math.round(sim * 1000) / 10.0); // 百分比，保留1位
                results.add(item);
            }
        }
        results.sort((a, b) -> Double.compare(
                (double) b.get("similarity"), (double) a.get("similarity")));
        return results.stream().limit(5).collect(Collectors.toList());
    }

    private static java.util.Set<String> bigrams(String text) {
        java.util.Set<String> set = new java.util.HashSet<>();
        if (text == null || text.length() < 2) return set;
        for (int i = 0; i < text.length() - 1; i++) {
            set.add(text.substring(i, i + 2));
        }
        return set;
    }

    private static double jaccardSimilarity(java.util.Set<String> a, java.util.Set<String> b) {
        if (a.isEmpty() && b.isEmpty()) return 1.0;
        if (a.isEmpty() || b.isEmpty()) return 0.0;
        long intersection = a.stream().filter(b::contains).count();
        long union = a.size() + b.size() - intersection;
        return union == 0 ? 0.0 : (double) intersection / union;
    }
}
