package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.ReviewScore;
import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.repository.ReviewScoreRepository;
import com.trae.pinguan.repository.ReviewTaskRepository;
import com.trae.pinguan.repository.SystemSettingRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.web.dto.ReviewFeedbackItem;
import com.trae.pinguan.web.dto.ReviewRankingItem;
import com.trae.pinguan.web.dto.ReviewAutoAssignRequest;
import com.trae.pinguan.web.dto.ReviewResultItem;
import com.trae.pinguan.web.dto.ReviewScoreRequest;
import com.trae.pinguan.web.dto.ReviewStageScoreSummary;
import com.trae.pinguan.web.dto.ReviewSummaryItem;
import com.trae.pinguan.web.dto.ReviewTaskAssignRequest;
import com.trae.pinguan.web.dto.ReviewTaskStatusRequest;
import com.trae.pinguan.web.dto.ReviewScoreReturnRequest;
import com.trae.pinguan.web.dto.ReviewerScoreDetail;
import com.trae.pinguan.web.dto.ScoreBreakdown;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ReviewService {
    private final ReviewTaskRepository reviewTaskRepository;
    private final ReviewScoreRepository reviewScoreRepository;
    private final RegistrationRepository registrationRepository;
    private final UserAccountRepository userAccountRepository;
    private final SystemSettingRepository systemSettingRepository;
    private final com.trae.pinguan.repository.ActivityInfoRepository activityInfoRepository;
    private final com.trae.pinguan.repository.DictionaryItemRepository dictionaryItemRepository;

    @Transactional
    public ReviewTask assignTask(ReviewTaskAssignRequest request) {
        Registration registration = registrationRepository.findById(request.getRegistrationId())
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        UserAccount reviewer = userAccountRepository.findById(request.getReviewerId())
                .orElseThrow(() -> new IllegalArgumentException("评审不存在"));
        if (reviewer.getInstitution() != null && registration.getInstitution() != null
                && reviewer.getInstitution().getId().equals(registration.getInstitution().getId())) {
            throw new IllegalArgumentException("同机构回避");
        }
        boolean duplicated = reviewTaskRepository.findByRegistrationId(registration.getId()).stream()
                .anyMatch(task -> task.getReviewer() != null && reviewer.getId().equals(task.getReviewer().getId()));
        if (duplicated) {
            throw new IllegalArgumentException("同一评委不得重复审同一项目");
        }
        int maxLoad = systemSettingRepository.findBySettingKey("reviewerMaxLoad")
                .map(setting -> Integer.parseInt(setting.getSettingValue()))
                .orElse(20);
        long currentLoad = reviewTaskRepository.findByReviewerId(reviewer.getId()).size();
        if (currentLoad >= maxLoad) {
            throw new IllegalArgumentException("评审负荷已满");
        }
        ReviewTask task = ReviewTask.builder()
                .registration(registration)
                .reviewer(reviewer)
                .stage(request.getStage())
                .status(ReviewStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .build();
        return reviewTaskRepository.save(task);
    }

    @Transactional
    public ReviewTask updateStatus(ReviewTaskStatusRequest request) {
        ReviewTask task = reviewTaskRepository.findById(request.getReviewTaskId())
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        task.setStatus(request.getStatus());
        return reviewTaskRepository.save(task);
    }

    @Transactional(readOnly = true)
    public List<ReviewTask> listTasks(Long reviewerId) {
        return reviewTaskRepository.findByReviewerId(reviewerId);
    }

    public List<ReviewTask> listTasks(Long reviewerId, ReviewStage stage, ReviewStatus status) {
        List<ReviewTask> tasks;
        if (stage != null) {
            tasks = reviewTaskRepository.findByReviewerIdAndStage(reviewerId, stage);
        } else {
            tasks = reviewTaskRepository.findByReviewerId(reviewerId);
        }
        if (status == null) {
            return tasks;
        }
        return tasks.stream().filter(task -> task.getStatus() == status).collect(Collectors.toList());
    }

    /**
     * 查询评审任务列表（支持分页）
     * 
     * @param competitionId 赛事ID
     * @param stage 评审阶段
     * @param status 任务状态
     * @param groupType 竞赛组别
     * @param groupCode 分组代码
     * @param reviewerId 评委ID
     * @param methodCode 品管工具代码
     * @param page 页码（从1开始），null表示不分页
     * @param size 每页数量，默认20
     * @return 不分页时返回List，分页时返回PageResult
     */
    @Transactional(readOnly = true)
    public Object listTasksByStage(
            Long competitionId, 
            ReviewStage stage, 
            ReviewStatus status,
            GroupType groupType,
            String groupCode,
            Long reviewerId,
            String methodCode,
            Integer page,
            Integer size) {
        
        // 如果不分页，使用原有逻辑
        if (page == null) {
            return listTasksWithoutPagination(competitionId, stage, status, groupType, groupCode, reviewerId, methodCode);
        }
        
        // 分页查询
        return listTasksWithPagination(competitionId, stage, status, groupType, groupCode, reviewerId, methodCode, page, size);
    }
    
    /**
     * 不分页查询（返回全部数据）
     */
    private List<com.trae.pinguan.web.dto.ReviewTaskItem> listTasksWithoutPagination(
            Long competitionId, ReviewStage stage, ReviewStatus status,
            GroupType groupType, String groupCode, Long reviewerId, String methodCode) {
        
        // 使用新的复杂查询方法
        List<ReviewTask> tasks = reviewTaskRepository.findTasksWithFilters(
                competitionId, stage, status, groupType, groupCode, reviewerId);
        
        // 如果有 methodCode 筛选，需要额外过滤（因为 methodCode 在 ActivityInfo 表中）
        if (methodCode != null && !methodCode.trim().isEmpty()) {
            final String methodCodeTrimmed = methodCode.trim();
            tasks = tasks.stream()
                    .filter(task -> {
                        com.trae.pinguan.domain.entity.ActivityInfo activityInfo = 
                                activityInfoRepository.findByRegistrationId(task.getRegistration().getId()).orElse(null);
                        return activityInfo != null && methodCodeTrimmed.equals(activityInfo.getMethodCode());
                    })
                    .collect(Collectors.toList());
        }
        
        // 转换为 DTO
        return tasks.stream()
                .map(this::convertToReviewTaskItem)
                .collect(Collectors.toList());
    }
    
    /**
     * 分页查询（返回PageResult）
     * 页码规范：前端传入从1开始，后端转换为Spring Data的从0开始
     */
    private com.trae.pinguan.web.dto.PageResult<com.trae.pinguan.web.dto.ReviewTaskItem> listTasksWithPagination(
            Long competitionId, ReviewStage stage, ReviewStatus status,
            GroupType groupType, String groupCode, Long reviewerId, String methodCode,
            Integer page, Integer size) {
        
        // 参数处理
        int actualPage = page != null && page > 0 ? page : 1;  // 确保page至少为1
        int pageNumber = actualPage - 1;  // 转换：1-based -> 0-based
        int pageSize = size != null && size > 0 ? size : 20;  // 默认20条/页
        
        // 创建分页对象
        org.springframework.data.domain.Pageable pageable = org.springframework.data.domain.PageRequest.of(
                pageNumber, pageSize, 
                org.springframework.data.domain.Sort.by(org.springframework.data.domain.Sort.Direction.DESC, "createdAt")
        );
        
        // 分页查询ID列表
        org.springframework.data.domain.Page<Long> taskIdPage = reviewTaskRepository.findTaskIdsWithFilters(
                competitionId, stage, status, groupType, groupCode, reviewerId, pageable);
        
        // 如果无数据，返回空分页结果
        if (taskIdPage.isEmpty()) {
            return com.trae.pinguan.web.dto.PageResult.<com.trae.pinguan.web.dto.ReviewTaskItem>builder()
                    .content(new ArrayList<>())
                    .pageNo(actualPage)
                    .pageSize(pageSize)
                    .totalCount(0L)
                    .totalPages(0)
                    .hasNext(false)
                    .hasPrevious(false)
                    .build();
        }
        
        // 根据ID列表获取完整数据（带JOIN FETCH）
        List<ReviewTask> tasks = reviewTaskRepository.findByIdsWithFetch(taskIdPage.getContent());
        
        // 如果有 methodCode 筛选，需要额外过滤
        // 注意：这里会影响分页的准确性，建议后续优化到SQL层
        if (methodCode != null && !methodCode.trim().isEmpty()) {
            final String methodCodeTrimmed = methodCode.trim();
            tasks = tasks.stream()
                    .filter(task -> {
                        com.trae.pinguan.domain.entity.ActivityInfo activityInfo = 
                                activityInfoRepository.findByRegistrationId(task.getRegistration().getId()).orElse(null);
                        return activityInfo != null && methodCodeTrimmed.equals(activityInfo.getMethodCode());
                    })
                    .collect(Collectors.toList());
        }
        
        // 转换为 DTO
        List<com.trae.pinguan.web.dto.ReviewTaskItem> items = tasks.stream()
                .map(this::convertToReviewTaskItem)
                .collect(Collectors.toList());
        
        // 构造分页结果（页码转换回1-based）
        return com.trae.pinguan.web.dto.PageResult.<com.trae.pinguan.web.dto.ReviewTaskItem>builder()
                .content(items)
                .pageNo(actualPage)
                .pageSize(pageSize)
                .totalCount(taskIdPage.getTotalElements())
                .totalPages(taskIdPage.getTotalPages())
                .hasNext(taskIdPage.hasNext())
                .hasPrevious(taskIdPage.hasPrevious())
                .build();
    }
    
    /**
     * 将ReviewTask转换为ReviewTaskItem DTO（提取公共方法）
     */
    private com.trae.pinguan.web.dto.ReviewTaskItem convertToReviewTaskItem(ReviewTask task) {
        Registration reg = task.getRegistration();
        UserAccount reviewer = task.getReviewer();
        
        // 获取 ActivityInfo 来填充品管工具信息
        com.trae.pinguan.domain.entity.ActivityInfo activityInfo = 
                activityInfoRepository.findByRegistrationId(reg.getId()).orElse(null);
        String method = activityInfo != null ? activityInfo.getMethodCode() : null;
        
        // 获取品管工具的 label
        String methodLabelValue = null;
        if (method != null) {
            methodLabelValue = dictionaryItemRepository.findFirstByTypeAndCodeAndActiveTrue("method", method)
                    .map(com.trae.pinguan.domain.entity.DictionaryItem::getLabel)
                    .orElse(null);
        }
        
        return com.trae.pinguan.web.dto.ReviewTaskItem.builder()
                .id(task.getId())
                .registrationId(reg != null ? reg.getId() : null)
                .projectName(reg != null ? reg.getProjectName() : null)
                .institutionName(reg != null && reg.getInstitution() != null 
                        ? reg.getInstitution().getName() : null)
                .institutionLevel(reg != null && reg.getInstitution() != null 
                        ? reg.getInstitution().getLevel() : null)
                .groupType(reg != null ? reg.getGroupType() : null)
                .groupCode(reg != null ? reg.getGroupCode() : null)
                .stage(task.getStage())
                .status(task.getStatus())
                .createdAt(task.getCreatedAt())
                .reviewerId(reviewer != null ? reviewer.getId() : null)
                .reviewerName(reviewer != null ? reviewer.getName() : null)
                .reviewerTitle(reviewer != null ? reviewer.getTitle() : null)
                .reviewerInstitutionName(reviewer != null && reviewer.getInstitution() != null 
                        ? reviewer.getInstitution().getName() : null)
                .methodCode(method)
                .methodLabel(methodLabelValue)
                .build();
    }

    @Transactional
    public List<ReviewTask> autoAssign(ReviewAutoAssignRequest request) {
        int perRegistration = request.getReviewersPerRegistration() == null ? 1 : request.getReviewersPerRegistration();
        int maxLoad = systemSettingRepository.findBySettingKey("reviewerMaxLoad")
                .map(setting -> Integer.parseInt(setting.getSettingValue()))
                .orElse(20);

        List<Registration> registrations = registrationRepository.findByCompetitionId(request.getCompetitionId());
        List<UserAccount> reviewers = userAccountRepository.findAll().stream()
                .filter(user -> user.getRole() == com.trae.pinguan.domain.enums.RoleType.REVIEWER)
                .collect(Collectors.toList());

        Map<Long, Integer> reviewerLoad = new HashMap<>();
        for (UserAccount reviewer : reviewers) {
            reviewerLoad.put(reviewer.getId(), reviewTaskRepository.findByReviewerId(reviewer.getId()).size());
        }

        List<ReviewTask> created = new ArrayList<>();
        int reviewerIndex = 0;
        for (Registration registration : registrations) {
            if (request.getStage() == ReviewStage.INTERVIEW && registration.getGroupType() != GroupType.ADVANCED) {
                continue;
            }
            if (!reviewTaskRepository.findByRegistrationIdAndStage(registration.getId(), request.getStage()).isEmpty()) {
                continue;
            }
            Set<Long> assignedReviewerIds = new HashSet<>();
            Set<String> assignedBackgrounds = new HashSet<>();
            for (ReviewTask task : reviewTaskRepository.findByRegistrationId(registration.getId())) {
                if (task.getReviewer() != null) {
                    assignedReviewerIds.add(task.getReviewer().getId());
                    if (task.getReviewer().getExpertBackground() != null) {
                        assignedBackgrounds.add(task.getReviewer().getExpertBackground());
                    }
                }
            }
            for (int i = 0; i < perRegistration; i++) {
                UserAccount selected = selectReviewer(reviewers, registration, request.getStage(),
                        assignedReviewerIds, assignedBackgrounds, reviewerLoad, maxLoad, reviewerIndex, perRegistration);
                if (selected == null) {
                    break;
                }
                ReviewTask task = ReviewTask.builder()
                        .registration(registration)
                        .reviewer(selected)
                        .stage(request.getStage())
                        .status(ReviewStatus.PENDING)
                        .createdAt(LocalDateTime.now())
                        .build();
                created.add(reviewTaskRepository.save(task));
                reviewerLoad.put(selected.getId(), reviewerLoad.get(selected.getId()) + 1);
                assignedReviewerIds.add(selected.getId());
                if (selected.getExpertBackground() != null) {
                    assignedBackgrounds.add(selected.getExpertBackground());
                }
                reviewerIndex = (reviewers.indexOf(selected) + 1) % Math.max(1, reviewers.size());
            }
        }
        return created;
    }

    private UserAccount selectReviewer(List<UserAccount> reviewers,
                                       Registration registration,
                                       ReviewStage stage,
                                       Set<Long> assignedReviewerIds,
                                       Set<String> assignedBackgrounds,
                                       Map<Long, Integer> reviewerLoad,
                                       int maxLoad,
                                       int startIndex,
                                       int perRegistration) {
        if (reviewers.isEmpty()) {
            return null;
        }
        String requiredGroup = resolveGroupCode(registration);
        boolean preferDifferentBackground = perRegistration > 1 && assignedBackgrounds.size() == 1;
        UserAccount selected = selectReviewerInternal(reviewers, registration, stage, assignedReviewerIds,
                assignedBackgrounds, reviewerLoad, maxLoad, startIndex, requiredGroup, preferDifferentBackground);
        if (selected != null) {
            return selected;
        }
        if (preferDifferentBackground) {
            return selectReviewerInternal(reviewers, registration, stage, assignedReviewerIds,
                    assignedBackgrounds, reviewerLoad, maxLoad, startIndex, requiredGroup, false);
        }
        return null;
    }

    private UserAccount selectReviewerInternal(List<UserAccount> reviewers,
                                               Registration registration,
                                               ReviewStage stage,
                                               Set<Long> assignedReviewerIds,
                                               Set<String> assignedBackgrounds,
                                               Map<Long, Integer> reviewerLoad,
                                               int maxLoad,
                                               int startIndex,
                                               String requiredGroup,
                                               boolean requireDifferentBackground) {
        for (int i = 0; i < reviewers.size(); i++) {
            int idx = (startIndex + i) % reviewers.size();
            UserAccount reviewer = reviewers.get(idx);
            if (stage == ReviewStage.INTERVIEW) {
                if (requiredGroup != null && (reviewer.getInterviewGroupCode() == null
                        || !requiredGroup.equals(reviewer.getInterviewGroupCode()))) {
                    continue;
                }
            } else {
                if (requiredGroup != null && (reviewer.getReviewerGroupCode() == null
                        || !requiredGroup.equals(reviewer.getReviewerGroupCode()))) {
                    continue;
                }
            }
            if (reviewer.getInstitution() != null && registration.getInstitution() != null
                    && reviewer.getInstitution().getId().equals(registration.getInstitution().getId())) {
                continue;
            }
            if (assignedReviewerIds.contains(reviewer.getId())) {
                continue;
            }
            if (requireDifferentBackground && reviewer.getExpertBackground() != null && assignedBackgrounds.size() == 1) {
                if (assignedBackgrounds.contains(reviewer.getExpertBackground())) {
                    continue;
                }
            }
            int load = reviewerLoad.getOrDefault(reviewer.getId(), 0);
            if (load >= maxLoad) {
                continue;
            }
            return reviewer;
        }
        return null;
    }

    private String resolveGroupCode(Registration registration) {
        if (registration.getGroupCode() != null && !registration.getGroupCode().trim().isEmpty()) {
            return registration.getGroupCode();
        }
        GroupType groupType = registration.getGroupType();
        if (groupType == null) {
            return null;
        }
        switch (groupType) {
            case BASIC:
                return "A1";
            case COMPREHENSIVE:
                return "B2";
            case ADVANCED:
                return "B2";
            default:
                return null;
        }
    }

    public Optional<ReviewScore> getScore(Long reviewTaskId) {
        return reviewScoreRepository.findByReviewTaskId(reviewTaskId);
    }

    @Transactional(readOnly = true)
    public List<ReviewResultItem> resultsByRegistration(Long registrationId) {
        List<ReviewResultItem> results = new ArrayList<>();
        for (ReviewStage stage : ReviewStage.values()) {
            List<ReviewTask> tasks = reviewTaskRepository.findByRegistrationIdAndStage(registrationId, stage);
            int taskCount = tasks.size();
            int scoredCount = 0;
            int totalSum = 0;
            for (ReviewTask task : tasks) {
                if (task.getStatus() != ReviewStatus.SCORED) {
                    continue;
                }
                ReviewScore score = reviewScoreRepository.findByReviewTaskId(task.getId()).orElse(null);
                if (score == null) {
                    continue;
                }
                scoredCount += 1;
                totalSum += score.getTotal();
            }
            Double avgTotal = scoredCount == 0 ? null : (double) totalSum / scoredCount;
            results.add(new ReviewResultItem(stage, taskCount, scoredCount, avgTotal));
        }
        return results;
    }

    @Transactional(readOnly = true)
    public List<ReviewStageScoreSummary> scoreSummaryByRegistration(Long registrationId) {
        List<ReviewStageScoreSummary> results = new ArrayList<>();
        for (ReviewStage stage : ReviewStage.values()) {
            List<ReviewTask> tasks = reviewTaskRepository.findByRegistrationIdAndStage(registrationId, stage);
            int taskCount = tasks.size();
            int scoredCount = 0;
            double planSum = 0;
            double problemSum = 0;
            double actionSum = 0;
            double successSum = 0;
            double reviewSum = 0;
            double operationSum = 0;
            double presentationSum = 0;
            double totalSum = 0;
            List<String> highlights = new ArrayList<>();
            List<String> weaknesses = new ArrayList<>();
            for (ReviewTask task : tasks) {
                if (task.getStatus() != ReviewStatus.SCORED) {
                    continue;
                }
                ReviewScore score = reviewScoreRepository.findByReviewTaskId(task.getId()).orElse(null);
                if (score == null) {
                    continue;
                }
                scoredCount += 1;
                planSum += score.getPlan();
                problemSum += score.getProblem();
                actionSum += score.getAction();
                successSum += score.getSuccess();
                reviewSum += score.getReview();
                operationSum += score.getOperation();
                presentationSum += score.getPresentation();
                totalSum += score.getTotal();
                if (score.getHighlight() != null && !score.getHighlight().trim().isEmpty()) {
                    highlights.add(score.getHighlight());
                }
                if (score.getWeakness() != null && !score.getWeakness().trim().isEmpty()) {
                    weaknesses.add(score.getWeakness());
                }
            }
            double divisor = scoredCount == 0 ? 1 : scoredCount;
            results.add(new ReviewStageScoreSummary(
                    stage,
                    taskCount,
                    scoredCount,
                    scoredCount == 0 ? null : planSum / divisor,
                    scoredCount == 0 ? null : problemSum / divisor,
                    scoredCount == 0 ? null : actionSum / divisor,
                    scoredCount == 0 ? null : successSum / divisor,
                    scoredCount == 0 ? null : reviewSum / divisor,
                    scoredCount == 0 ? null : operationSum / divisor,
                    scoredCount == 0 ? null : presentationSum / divisor,
                    scoredCount == 0 ? null : totalSum / divisor,
                    highlights,
                    weaknesses
            ));
        }
        return results;
    }

    @Transactional(readOnly = true)
    public List<ReviewFeedbackItem> feedbackByStage(Long competitionId, ReviewStage stage) {
        List<ReviewTask> tasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(stage, competitionId);
        List<ReviewFeedbackItem> items = new ArrayList<>();
        for (ReviewTask task : tasks) {
            if (task.getStatus() != ReviewStatus.SCORED) {
                continue;
            }
            ReviewScore score = reviewScoreRepository.findByReviewTaskId(task.getId()).orElse(null);
            if (score == null) {
                continue;
            }
            items.add(new ReviewFeedbackItem(
                    task.getRegistration().getId(),
                    task.getRegistration().getProjectName(),
                    task.getRegistration().getInstitution().getName(),
                    stage,
                    task.getReviewer() == null ? null : task.getReviewer().getId(),
                    task.getReviewer() == null ? null : task.getReviewer().getName(),
                    task.getReviewer() == null ? null : task.getReviewer().getTitle(),
                    score.getTotal(),
                    score.getHighlight(),
                    score.getWeakness()
            ));
        }
        return items;
    }

    @Transactional
    public ReviewScore submitScore(ReviewScoreRequest request) {
        ReviewTask task = reviewTaskRepository.findById(request.getReviewTaskId())
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        int total = request.getPlan() + request.getProblem() + request.getAction()
                + request.getSuccess() + request.getReview() + request.getOperation()
                + request.getPresentation();
        ReviewScore score = reviewScoreRepository.findByReviewTaskId(task.getId())
                .orElse(ReviewScore.builder().reviewTask(task).build());
        score.setPlan(request.getPlan());
        score.setProblem(request.getProblem());
        score.setAction(request.getAction());
        score.setSuccess(request.getSuccess());
        score.setReview(request.getReview());
        score.setOperation(request.getOperation());
        score.setPresentation(request.getPresentation());
        score.setTotal(total);
        score.setHighlight(request.getHighlight());
        score.setWeakness(request.getWeakness());
        score.setSubmittedAt(LocalDateTime.now());
        ReviewScore saved = reviewScoreRepository.save(score);
        task.setStatus(ReviewStatus.SCORED);
        reviewTaskRepository.save(task);
        return saved;
    }

    @Transactional
    public ReviewTask returnScore(ReviewScoreReturnRequest request) {
        ReviewTask task = reviewTaskRepository.findById(request.getReviewTaskId())
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        if (task.getStatus() != ReviewStatus.SCORED) {
            throw new IllegalArgumentException("评审未完成");
        }
        String publishKey = "publish_" + task.getRegistration().getCompetition().getId() + "_" + task.getStage().name();
        boolean published = systemSettingRepository.findBySettingKey(publishKey)
                .map(setting -> "true".equalsIgnoreCase(setting.getSettingValue()))
                .orElse(false);
        if (published) {
            throw new IllegalArgumentException("已公布无法退回");
        }
        reviewScoreRepository.findByReviewTaskId(task.getId()).ifPresent(reviewScoreRepository::delete);
        task.setStatus(ReviewStatus.RETURNED);
        return reviewTaskRepository.save(task);
    }

    @Transactional(readOnly = true)
    public List<ReviewSummaryItem> summaryByStage(Long competitionId, ReviewStage stage) {
        List<ReviewTask> tasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(stage, competitionId);
        Map<Long, SummaryAccumulator> accumulators = new HashMap<>();
        for (ReviewTask task : tasks) {
            if (task.getStatus() != ReviewStatus.SCORED) {
                continue;
            }
            ReviewScore score = reviewScoreRepository.findByReviewTaskId(task.getId()).orElse(null);
            if (score == null) {
                continue;
            }
            Long registrationId = task.getRegistration().getId();
            SummaryAccumulator acc = accumulators.computeIfAbsent(registrationId, id -> new SummaryAccumulator(task));
            acc.add(score.getTotal());
        }
        List<ReviewSummaryItem> result = new ArrayList<>();
        for (SummaryAccumulator acc : accumulators.values()) {
            result.add(new ReviewSummaryItem(
                    acc.registrationId,
                    acc.projectName,
                    acc.institutionName,
                    acc.institutionLevel,
                    acc.groupType,
                    stage,
                    acc.avg(),
                    acc.count
            ));
        }
        return result;
    }

    @Transactional(readOnly = true)
    /**
     * 查询评分排名（支持分页）
     * 
     * @param competitionId 赛事ID
     * @param stage 评审阶段
     * @param groupType 竞赛组别
     * @param page 页码（从1开始），null表示不分页
     * @param size 每页数量，默认20
     * @return 不分页时返回List，分页时返回PageResult
     */
    public Object rankingByStage(Long competitionId, ReviewStage stage, GroupType groupType, 
                                 Integer page, Integer size) {
        // 如果不分页，使用原有逻辑
        if (page == null) {
            return rankingByStageWithoutPagination(competitionId, stage, groupType);
        }
        
        // 分页查询
        return rankingByStageWithPagination(competitionId, stage, groupType, page, size);
    }
    
    /**
     * 不分页查询（保留原有逻辑）
     */
    private List<ReviewRankingItem> rankingByStageWithoutPagination(Long competitionId, ReviewStage stage, GroupType groupType) {
        List<ReviewSummaryItem> summary = summaryByStage(competitionId, stage);
        List<ReviewSummaryItem> filtered = summary.stream()
                .filter(item -> groupType == null || item.getGroupType() == groupType)
                .sorted(Comparator.comparing(ReviewSummaryItem::getAvgTotal).reversed())
                .collect(Collectors.toList());
        List<ReviewRankingItem> ranking = new ArrayList<>();
        int rank = 1;
        for (ReviewSummaryItem item : filtered) {
            ranking.add(new ReviewRankingItem(
                    rank++,
                    item.getRegistrationId(),
                    item.getProjectName(),
                    item.getInstitutionName(),
                    item.getInstitutionLevel(),
                    item.getGroupType(),
                    item.getStage(),
                    item.getAvgTotal()
            ));
        }
        return ranking;
    }
    
    /**
     * 分页查询（页码从1开始）
     */
    private com.trae.pinguan.web.dto.PageResult<ReviewRankingItem> rankingByStageWithPagination(
            Long competitionId, ReviewStage stage, GroupType groupType, Integer page, Integer size) {
        
        // 获取全部排名数据
        List<ReviewRankingItem> allRankings = rankingByStageWithoutPagination(competitionId, stage, groupType);
        
        // 参数处理
        int actualPage = page != null && page > 0 ? page : 1;
        int pageSize = size != null && size > 0 ? size : 20;
        
        // 计算分页
        int totalCount = allRankings.size();
        int totalPages = (int) Math.ceil((double) totalCount / pageSize);
        int startIndex = (actualPage - 1) * pageSize;
        int endIndex = Math.min(startIndex + pageSize, totalCount);
        
        // 如果页码超出范围，返回空结果
        if (startIndex >= totalCount) {
            return com.trae.pinguan.web.dto.PageResult.<ReviewRankingItem>builder()
                    .content(new ArrayList<>())
                    .pageNo(actualPage)
                    .pageSize(pageSize)
                    .totalCount((long) totalCount)
                    .totalPages(totalPages)
                    .hasNext(false)
                    .hasPrevious(actualPage > 1)
                    .build();
        }
        
        // 提取当前页数据
        List<ReviewRankingItem> pageData = allRankings.subList(startIndex, endIndex);
        
        // 构造分页结果
        return com.trae.pinguan.web.dto.PageResult.<ReviewRankingItem>builder()
                .content(pageData)
                .pageNo(actualPage)
                .pageSize(pageSize)
                .totalCount((long) totalCount)
                .totalPages(totalPages)
                .hasNext(endIndex < totalCount)
                .hasPrevious(actualPage > 1)
                .build();
    }
    
    /**
     * 入围名单分页查询
     */
    public com.trae.pinguan.web.dto.PageResult<ReviewRankingItem> shortlistWithPagination(
            Long competitionId, ReviewStage stage, GroupType groupType, 
            Double minAvgTotal, Integer page, Integer size) {
        
        // 获取全部排名数据
        List<ReviewRankingItem> allRankings = rankingByStageWithoutPagination(competitionId, stage, groupType);
        
        // 按分数线筛选
        List<ReviewRankingItem> filtered = allRankings.stream()
                .filter(item -> minAvgTotal == null || item.getAvgTotal() >= minAvgTotal)
                .collect(Collectors.toList());
        
        // 参数处理
        int actualPage = page != null && page > 0 ? page : 1;
        int pageSize = size != null && size > 0 ? size : 20;
        
        // 计算分页
        int totalCount = filtered.size();
        int totalPages = (int) Math.ceil((double) totalCount / pageSize);
        int startIndex = (actualPage - 1) * pageSize;
        int endIndex = Math.min(startIndex + pageSize, totalCount);
        
        // 如果页码超出范围，返回空结果
        if (startIndex >= totalCount) {
            return com.trae.pinguan.web.dto.PageResult.<ReviewRankingItem>builder()
                    .content(new ArrayList<>())
                    .pageNo(actualPage)
                    .pageSize(pageSize)
                    .totalCount((long) totalCount)
                    .totalPages(totalPages)
                    .hasNext(false)
                    .hasPrevious(actualPage > 1)
                    .build();
        }
        
        // 提取当前页数据
        List<ReviewRankingItem> pageData = filtered.subList(startIndex, endIndex);
        
        // 构造分页结果
        return com.trae.pinguan.web.dto.PageResult.<ReviewRankingItem>builder()
                .content(pageData)
                .pageNo(actualPage)
                .pageSize(pageSize)
                .totalCount((long) totalCount)
                .totalPages(totalPages)
                .hasNext(endIndex < totalCount)
                .hasPrevious(actualPage > 1)
                .build();
    }

    private static class SummaryAccumulator {
        private final Long registrationId;
        private final String projectName;
        private final String institutionName;
        private final String institutionLevel;
        private final GroupType groupType;
        private int count;
        private int totalSum;

        private SummaryAccumulator(ReviewTask task) {
            this.registrationId = task.getRegistration().getId();
            this.projectName = task.getRegistration().getProjectName();
            this.institutionName = task.getRegistration().getInstitution().getName();
            this.institutionLevel = task.getRegistration().getInstitution().getLevel();
            this.groupType = task.getRegistration().getGroupType();
        }

        private void add(int total) {
            this.totalSum += total;
            this.count += 1;
        }

        private double avg() {
            if (count == 0) {
                return 0;
            }
            return (double) totalSum / count;
        }
    }

    /**
     * 获取指定项目的评委评分详情
     * @param registrationId 报名ID
     * @param stage 评审阶段（可选）
     * @return 评委评分详情列表
     */
    @Transactional(readOnly = true)
    public List<ReviewerScoreDetail> getReviewerScoresByRegistration(Long registrationId, ReviewStage stage) {
        List<ReviewerScoreDetail> results = new ArrayList<>();
        
        // 构建查询条件
        List<ReviewTask> tasks;
        if (stage == null) {
            tasks = reviewTaskRepository.findByRegistrationId(registrationId);
        } else {
            tasks = reviewTaskRepository.findByRegistrationIdAndStage(registrationId, stage);
        }
        
        // 遍历评审任务
        for (ReviewTask task : tasks) {
            // 只处理已评分的任务
            if (task.getStatus() != ReviewStatus.SCORED) {
                continue;
            }
            
            // 获取评分记录
            ReviewScore score = reviewScoreRepository
                .findByReviewTaskId(task.getId())
                .orElse(null);
            if (score == null) {
                continue;
            }
            
            // 获取评委信息
            UserAccount reviewer = task.getReviewer();
            if (reviewer == null) {
                continue;
            }
            
            Institution institution = reviewer.getInstitution();
            
            // 构建返回对象
            results.add(ReviewerScoreDetail.builder()
                .stage(task.getStage())
                .reviewerId(reviewer.getId())
                .reviewerName(reviewer.getName())
                .reviewerTitle(reviewer.getTitle())
                .reviewerInstitutionId(institution == null ? null : institution.getId())
                .reviewerInstitutionName(institution == null ? null : institution.getName())
                .reviewerInstitutionLevel(institution == null ? null : institution.getLevel())
                .scores(ScoreBreakdown.builder()
                    .plan(score.getPlan())
                    .problem(score.getProblem())
                    .action(score.getAction())
                    .success(score.getSuccess())
                    .review(score.getReview())
                    .operation(score.getOperation())
                    .presentation(score.getPresentation())
                    .total(score.getTotal())
                    .build())
                .highlight(score.getHighlight())
                .weakness(score.getWeakness())
                .submittedAt(score.getSubmittedAt())
                .build());
        }
        
        // 按阶段、评委ID排序
        results.sort(Comparator
            .comparing(ReviewerScoreDetail::getStage)
            .thenComparing(ReviewerScoreDetail::getReviewerId));
        
        return results;
    }
}
