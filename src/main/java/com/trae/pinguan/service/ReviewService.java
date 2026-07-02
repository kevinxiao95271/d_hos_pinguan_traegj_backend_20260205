package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.entity.InterviewScore;
import com.trae.pinguan.domain.entity.ProjectFeedback;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.ReviewScore;
import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.entity.ScoringSnapshot;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import com.trae.pinguan.repository.InterviewScoreRepository;
import com.trae.pinguan.repository.ProjectFeedbackRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.repository.ReviewScoreRepository;
import com.trae.pinguan.repository.ReviewTaskRepository;
import com.trae.pinguan.repository.ScoringSnapshotRepository;
import com.trae.pinguan.repository.SystemSettingRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.InterviewScoreRequest;
import com.trae.pinguan.web.dto.ProjectFeedbackFilterOptionsResponse;
import com.trae.pinguan.web.dto.ProjectFeedbackItem;
import com.trae.pinguan.web.dto.ProjectFeedbackUpdateRequest;
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
import com.trae.pinguan.web.dto.ScoreListItem;
import com.trae.pinguan.web.dto.ScoreListItem.ReviewerScoreDetail;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalDouble;
import java.util.Set;
import java.util.stream.Collectors;
import java.sql.Timestamp;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ReviewService {
    private final ReviewTaskRepository reviewTaskRepository;
    private final ReviewScoreRepository reviewScoreRepository;
    private final InterviewScoreRepository interviewScoreRepository;
    private final ProjectFeedbackRepository projectFeedbackRepository;
    private final ScoringSnapshotRepository scoringSnapshotRepository;
    private final RegistrationRepository registrationRepository;
    private final UserAccountRepository userAccountRepository;
    private final SystemSettingRepository systemSettingRepository;
    private final JdbcTemplate jdbcTemplate;
    private final ComputeJobTracker computeJobTracker;

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
        LocalDateTime now = LocalDateTime.now();
        ReviewTask task = ReviewTask.builder()
                .registration(registration)
                .reviewer(reviewer)
                .stage(request.getStage())
                .status(ReviewStatus.PENDING)
                .createdAt(now)
                .updatedAt(now)
                .build();
        return reviewTaskRepository.save(task);
    }

    @Transactional
    public ReviewTask updateStatus(ReviewTaskStatusRequest request) {
        ReviewTask task = reviewTaskRepository.findById(request.getReviewTaskId())
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        task.setStatus(request.getStatus());
        task.setUpdatedAt(LocalDateTime.now());
        return reviewTaskRepository.save(task);
    }

    @Transactional(readOnly = true)
    public List<ReviewTask> listTasks(Long reviewerId) {
        return reviewTaskRepository.findByReviewerId(reviewerId);
    }

    @Transactional(readOnly = true)
    public List<com.trae.pinguan.web.dto.ReviewTaskItem> myTaskItems(Long reviewerId) {
        List<ReviewTask> tasks = reviewTaskRepository.findByReviewerId(reviewerId);
        Set<Long> taskIds = tasks.stream().map(ReviewTask::getId).collect(Collectors.toSet());

        Map<Long, Double> totalMap = new HashMap<>();
        if (!taskIds.isEmpty()) {
            reviewScoreRepository.findByReviewTaskIdIn(taskIds)
                    .forEach(s -> { if (s.getTotal() != null) totalMap.put(s.getReviewTaskId(), s.getTotal()); });
            interviewScoreRepository.findByReviewTaskIdIn(taskIds)
                    .forEach(s -> { if (s.getTotal() != null) totalMap.put(s.getReviewTaskId(), s.getTotal()); });
        }

        // 排序优先级：草稿(有分值) > 已提交 > 其他(待评/退回) > 规避
        // 同优先级内按 total 倒序，无分值排末位
        java.util.Comparator<com.trae.pinguan.web.dto.ReviewTaskItem> comparator =
            java.util.Comparator
                .<com.trae.pinguan.web.dto.ReviewTaskItem, Integer>comparing(item -> {
                    ReviewStatus s = item.getStatus();
                    if (s == ReviewStatus.DRAFT)   return 0;
                    if (s == ReviewStatus.SCORED)  return 1;
                    if (s == ReviewStatus.RECUSED) return 3;
                    return 2; // PENDING / CONFIRMED / RETURNED
                })
                .thenComparing(item -> item.getTotal() != null ? -item.getTotal() : Double.MAX_VALUE)
                .thenComparingLong(com.trae.pinguan.web.dto.ReviewTaskItem::getId);

        return tasks.stream().map(task -> {
            Registration reg = task.getRegistration();
            return com.trae.pinguan.web.dto.ReviewTaskItem.builder()
                    .id(task.getId())
                    .registrationId(reg != null ? reg.getId() : null)
                    .projectName(reg != null ? reg.getProjectName() : null)
                    .institutionName(reg != null && reg.getInstitution() != null
                            ? reg.getInstitution().getName() : null)
                    .institutionLevel(reg != null && reg.getInstitution() != null
                            ? reg.getInstitution().getLevel() : null)
                    .stage(task.getStage())
                    .status(task.getStatus())
                    .createdAt(task.getCreatedAt())
                    .total(totalMap.get(task.getId()))
                    .recuseReasonCode(task.getRecuseReasonCode())
                    .recuseReasonOther(task.getRecuseReasonOther())
                    .build();
        }).sorted(comparator).collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Map<String, Long> myTaskStats(Long reviewerId) {
        List<ReviewTask> tasks = reviewTaskRepository.findByReviewerId(reviewerId);
        long total = tasks.size();
        long scored = tasks.stream().filter(t -> t.getStatus() == ReviewStatus.SCORED).count();
        long recused = tasks.stream().filter(t -> t.getStatus() == ReviewStatus.RECUSED).count();
        long pendingSubmit = tasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.PENDING
                        || t.getStatus() == ReviewStatus.CONFIRMED
                        || t.getStatus() == ReviewStatus.DRAFT
                        || t.getStatus() == ReviewStatus.RETURNED)
                .count();
        Map<String, Long> stats = new java.util.LinkedHashMap<>();
        stats.put("total", total);
        stats.put("pendingSubmit", pendingSubmit);
        stats.put("scored", scored);
        stats.put("recused", recused);
        return stats;
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

    public List<ReviewTask> listTasksByStage(Long competitionId, ReviewStage stage, ReviewStatus status) {
        if (status == null) {
            return reviewTaskRepository.findByStageAndRegistrationCompetitionId(stage, competitionId);
        }
        return reviewTaskRepository.findByStageAndStatusAndRegistrationCompetitionId(stage, status, competitionId);
    }

    @Transactional(readOnly = true)
    public List<com.trae.pinguan.web.dto.AdminReviewTaskItem> listTasksForAdmin(
            Long competitionId, ReviewStage stage, ReviewStatus status, String reviewerName) {
        List<ReviewTask> tasks;
        if (status == null) {
            tasks = reviewTaskRepository.findWithDetailsByStageAndCompetitionId(stage, competitionId);
        } else {
            tasks = reviewTaskRepository.findWithDetailsByStageAndStatusAndCompetitionId(stage, status, competitionId);
        }

        return tasks.stream()
                .filter(task -> {
                    if (reviewerName == null || reviewerName.trim().isEmpty()) return true;
                    UserAccount reviewer = task.getReviewer();
                    return reviewer != null && reviewer.getName() != null
                            && reviewer.getName().contains(reviewerName.trim());
                })
                .map(task -> {
                    Registration reg = task.getRegistration();
                    UserAccount reviewer = task.getReviewer();
                    
                    return com.trae.pinguan.web.dto.AdminReviewTaskItem.builder()
                            .id(task.getId())
                            .stage(task.getStage())
                            .status(task.getStatus())
                            .createdAt(task.getCreatedAt())
                            .updatedAt(task.getUpdatedAt())
                            // 报名信息
                            .registrationId(reg != null ? reg.getId() : null)
                            .projectName(reg != null ? reg.getProjectName() : null)
                            .institutionName(reg != null && reg.getInstitution() != null 
                                    ? reg.getInstitution().getName() : null)
                            .groupType(reg != null ? reg.getGroupType() : null)
                            .groupCode(reg != null ? reg.getGroupCode() : null)
                            // 评委信息
                            .reviewerId(reviewer != null ? reviewer.getId() : null)
                            .reviewerName(reviewer != null ? reviewer.getName() : null)
                            .reviewerTitle(reviewer != null ? reviewer.getTitle() : null)
                            .reviewerInstitutionName(reviewer != null && reviewer.getInstitution() != null 
                                    ? reviewer.getInstitution().getName() : null)
                            .reviewerGroupCode(reviewer != null ? reviewer.getReviewerGroupCode() : null)
                            .interviewGroupCode(reviewer != null ? reviewer.getInterviewGroupCode() : null)
                            .expertBackground(reviewer != null ? reviewer.getExpertBackground() : null)
                            .build();
                })
                .collect(Collectors.toList());
    }

    @Transactional
    public List<ReviewTask> autoAssign(ReviewAutoAssignRequest request) {
        int perRegistration = request.getReviewersPerRegistration() == null ? 1 : request.getReviewersPerRegistration();
        int maxLoad = systemSettingRepository.findBySettingKey("reviewerMaxLoad")
                .map(setting -> Integer.parseInt(setting.getSettingValue()))
                .orElse(20);

        List<Registration> registrations = registrationRepository.findByCompetitionId(request.getCompetitionId());
        List<UserAccount> reviewers = userAccountRepository.findByRoleWithInstitution(com.trae.pinguan.domain.enums.RoleType.REVIEWER);

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
        // groupCode 未分配时，用赛事配置的前缀 + "1" 作为兜底（不写死字母）
        GroupType groupType = registration.getGroupType();
        if (groupType == null || registration.getCompetition() == null) {
            return null;
        }
        Competition competition = registration.getCompetition();
        String prefix;
        switch (groupType) {
            case BASIC:
                prefix = competition.getBasicGroupPrefix() != null ? competition.getBasicGroupPrefix().toUpperCase() : "A";
                break;
            case COMPREHENSIVE:
                prefix = competition.getComprehensiveGroupPrefix() != null ? competition.getComprehensiveGroupPrefix().toUpperCase() : "B";
                break;
            case ADVANCED:
                prefix = competition.getAdvancedGroupPrefix() != null ? competition.getAdvancedGroupPrefix().toUpperCase() : "C";
                break;
            default:
                return null;
        }
        return prefix + "1";
    }

    public Optional<ReviewScore> getScore(Long reviewTaskId) {
        return reviewScoreRepository.findByReviewTaskId(reviewTaskId);
    }

    @Transactional(readOnly = true)
    public List<ReviewResultItem> resultsByRegistration(Long registrationId) {
        // 一次查出所有任务，按stage分组，批量加载评分，避免N次单独查询
        List<ReviewTask> allTasks = reviewTaskRepository.findByRegistrationId(registrationId);
        Set<Long> scoredTaskIds = allTasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                .map(ReviewTask::getId)
                .collect(Collectors.toSet());
        Map<Long, ReviewScore> scoreMap = new HashMap<>();
        if (!scoredTaskIds.isEmpty()) {
            reviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                    .forEach(s -> scoreMap.put(s.getReviewTaskId(), s));
        }
        Map<ReviewStage, List<ReviewTask>> tasksByStage = allTasks.stream()
                .collect(Collectors.groupingBy(ReviewTask::getStage));
        List<ReviewResultItem> results = new ArrayList<>();
        for (ReviewStage stage : ReviewStage.values()) {
            List<ReviewTask> tasks = tasksByStage.getOrDefault(stage, Collections.emptyList());
            int taskCount = tasks.size();
            int scoredCount = 0;
            int totalSum = 0;
            for (ReviewTask task : tasks) {
                if (task.getStatus() != ReviewStatus.SCORED) continue;
                ReviewScore score = scoreMap.get(task.getId());
                if (score == null) continue;
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
        List<ReviewTask> allTasks = reviewTaskRepository.findByRegistrationId(registrationId);
        Set<Long> scoredTaskIds = allTasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                .map(ReviewTask::getId)
                .collect(Collectors.toSet());

        // 书审评分 map
        Map<Long, ReviewScore> bookScoreMap = new HashMap<>();
        if (!scoredTaskIds.isEmpty()) {
            reviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                    .forEach(s -> bookScoreMap.put(s.getReviewTaskId(), s));
        }
        // 面谈评分 map
        Map<Long, com.trae.pinguan.domain.entity.InterviewScore> intScoreMap = new HashMap<>();
        if (!scoredTaskIds.isEmpty()) {
            interviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                    .forEach(s -> intScoreMap.put(s.getReviewTaskId(), s));
        }

        Map<ReviewStage, List<ReviewTask>> tasksByStage = allTasks.stream()
                .collect(Collectors.groupingBy(ReviewTask::getStage));
        List<ReviewStageScoreSummary> results = new ArrayList<>();

        for (ReviewStage stage : ReviewStage.values()) {
            List<ReviewTask> tasks = tasksByStage.getOrDefault(stage, Collections.emptyList());
            int taskCount = tasks.size();
            int scoredCount = 0;
            List<String> highlights = new ArrayList<>();
            List<String> weaknesses = new ArrayList<>();

            if (stage == ReviewStage.INTERVIEW) {
                double topicSum = 0, processSum = 0, opSum = 0, resultSum = 0, totalSum = 0;
                List<ReviewerScoreDetail> reviewerScores = new ArrayList<>();
                for (ReviewTask task : tasks) {
                    com.trae.pinguan.domain.entity.InterviewScore s = intScoreMap.get(task.getId());
                    ReviewerScoreDetail.ReviewerScoreDetailBuilder rb = ReviewerScoreDetail.builder()
                            .reviewTaskId(task.getId())
                            .reviewerId(task.getReviewer() != null ? task.getReviewer().getId() : null)
                            .reviewerName(task.getReviewer() != null ? task.getReviewer().getName() : null)
                            .status(task.getStatus().name());
                    if (task.getStatus() == ReviewStatus.SCORED && s != null) {
                        rb.topic(s.getTopic()).process(s.getProcess())
                          .interviewOperation(s.getOperation()).result(s.getResult())
                          .total(s.getTotal())
                          .submittedAt(s.getSubmittedAt());
                        scoredCount++;
                        topicSum   += s.getTopic();
                        processSum += s.getProcess();
                        opSum      += s.getOperation();
                        resultSum  += s.getResult();
                        totalSum   += s.getTotal();
                    }
                    reviewerScores.add(rb.build());
                }
                double d = scoredCount == 0 ? 1 : scoredCount;
                results.add(ReviewStageScoreSummary.builder()
                        .stage(stage).taskCount(taskCount).scoredCount(scoredCount)
                        .avgTopic(scoredCount == 0 ? null : topicSum / d)
                        .avgProcess(scoredCount == 0 ? null : processSum / d)
                        .avgInterviewOperation(scoredCount == 0 ? null : opSum / d)
                        .avgResult(scoredCount == 0 ? null : resultSum / d)
                        .avgTotal(scoredCount == 0 ? null : totalSum / d)
                        .highlights(highlights).weaknesses(weaknesses)
                        .reviewerScores(reviewerScores)
                        .build());
            } else {
                double planSum = 0, problemSum = 0, actionSum = 0, successSum = 0,
                       reviewSum = 0, operationSum = 0, presentationSum = 0, totalSum = 0;
                for (ReviewTask task : tasks) {
                    if (task.getStatus() != ReviewStatus.SCORED) continue;
                    ReviewScore score = bookScoreMap.get(task.getId());
                    if (score == null) continue;
                    scoredCount++;
                    planSum         += score.getPlan();
                    problemSum      += score.getProblem();
                    actionSum       += score.getAction();
                    successSum      += score.getSuccess();
                    reviewSum       += score.getReview();
                    operationSum    += score.getOperation();
                    presentationSum += score.getPresentation();
                    totalSum        += score.getTotal();
                    if (score.getHighlight() != null && !score.getHighlight().trim().isEmpty()) highlights.add(score.getHighlight());
                    if (score.getWeakness()  != null && !score.getWeakness().trim().isEmpty())  weaknesses.add(score.getWeakness());
                }
                double d = scoredCount == 0 ? 1 : scoredCount;
                results.add(ReviewStageScoreSummary.builder()
                        .stage(stage).taskCount(taskCount).scoredCount(scoredCount)
                        .avgPlan(scoredCount == 0 ? null : planSum / d)
                        .avgProblem(scoredCount == 0 ? null : problemSum / d)
                        .avgAction(scoredCount == 0 ? null : actionSum / d)
                        .avgSuccess(scoredCount == 0 ? null : successSum / d)
                        .avgReview(scoredCount == 0 ? null : reviewSum / d)
                        .avgOperation(scoredCount == 0 ? null : operationSum / d)
                        .avgPresentation(scoredCount == 0 ? null : presentationSum / d)
                        .avgTotal(scoredCount == 0 ? null : totalSum / d)
                        .highlights(highlights).weaknesses(weaknesses)
                        .build());
            }
        }
        return results;
    }

    @Transactional(readOnly = true)
    public List<ReviewFeedbackItem> feedbackByStage(Long competitionId, ReviewStage stage) {
        List<ReviewTask> tasks = reviewTaskRepository.findWithDetailsByStageAndCompetitionId(stage, competitionId);
        // 批量加载评分，避免N次单独查询
        Set<Long> scoredTaskIds = tasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                .map(ReviewTask::getId)
                .collect(Collectors.toSet());
        Map<Long, ReviewScore> scoreMap = new HashMap<>();
        if (!scoredTaskIds.isEmpty()) {
            reviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                    .forEach(s -> scoreMap.put(s.getReviewTaskId(), s));
        }
        List<ReviewFeedbackItem> items = new ArrayList<>();
        for (ReviewTask task : tasks) {
            if (task.getStatus() != ReviewStatus.SCORED) {
                continue;
            }
            ReviewScore score = scoreMap.get(task.getId());
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
                    score.getTotal(),
                    score.getHighlight(),
                    score.getWeakness()
            ));
        }
        return items;
    }

    @Transactional
    public List<ProjectFeedbackItem> projectFeedbacksByStage(Long competitionId, ReviewStage stage) {
        return projectFeedbacksByStage(competitionId, stage, null, null, null, null, null, false);
    }

    @Transactional
    public List<ProjectFeedbackItem> projectFeedbacksByStage(Long competitionId,
                                                             ReviewStage stage,
                                                             GroupType groupType,
                                                             String groupCode,
                                                             String projectName,
                                                             String institutionName,
                                                             Boolean published) {
        return projectFeedbacksByStage(competitionId, stage, groupType, groupCode, projectName, institutionName, published, false);
    }

    @Transactional
    public List<ProjectFeedbackItem> projectFeedbacksByStage(Long competitionId,
                                                             ReviewStage stage,
                                                             GroupType groupType,
                                                             String groupCode,
                                                             String projectName,
                                                             String institutionName,
                                                             Boolean published,
                                                             boolean refresh) {
        ensureFeedbackSupportedStage(stage);
        long existingCount = projectFeedbackRepository.countByCompetitionIdAndStage(competitionId, stage);
        if (refresh || existingCount == 0L) {
            List<ReviewTask> tasks = reviewTaskRepository.findWithDetailsByStageAndCompetitionId(stage, competitionId);
            Map<Long, FeedbackSource> sourceMap = buildFeedbackSourceMap(tasks);
            upsertProjectFeedbackSources(sourceMap, stage, null);
        }
        List<ProjectFeedback> feedbacks = projectFeedbackRepository.findFilteredByCompetitionAndStageWithRegistration(
                competitionId,
                stage,
                groupType,
                normalize(groupCode),
                normalize(projectName),
                normalize(institutionName),
                published);
        return feedbacks.stream()
                .sorted(Comparator.comparing((ProjectFeedback pf) -> pf.getRegistration().getId()))
                .map(this::toProjectFeedbackItem)
                .collect(Collectors.toList());
    }

    @Transactional
    public ProjectFeedbackFilterOptionsResponse projectFeedbackFilterOptions(Long competitionId,
                                                                            ReviewStage stage,
                                                                            GroupType groupType) {
        ensureFeedbackSupportedStage(stage);
        List<ProjectFeedbackItem> items = projectFeedbacksByStage(competitionId, stage);
        Map<GroupType, Set<String>> codeSetMap = new java.util.LinkedHashMap<>();
        for (ProjectFeedbackItem item : items) {
            if (item.getGroupType() == null) {
                continue;
            }
            codeSetMap.computeIfAbsent(item.getGroupType(), k -> new java.util.LinkedHashSet<>());
            if (item.getGroupCode() != null && !item.getGroupCode().trim().isEmpty()) {
                codeSetMap.get(item.getGroupType()).add(item.getGroupCode().trim());
            }
        }

        Map<GroupType, List<String>> groupCodesByGroupType = new java.util.LinkedHashMap<>();
        for (Map.Entry<GroupType, Set<String>> entry : codeSetMap.entrySet()) {
            groupCodesByGroupType.put(entry.getKey(), new ArrayList<>(entry.getValue()));
        }

        List<GroupType> groupTypes = new ArrayList<>(groupCodesByGroupType.keySet());
        List<String> groupCodes = groupType == null
                ? groupCodesByGroupType.values().stream().flatMap(List::stream).distinct().collect(Collectors.toList())
                : groupCodesByGroupType.getOrDefault(groupType, Collections.emptyList());

        return ProjectFeedbackFilterOptionsResponse.builder()
                .groupTypes(groupTypes)
                .groupCodesByGroupType(groupCodesByGroupType)
                .groupCodes(groupCodes)
                .build();
    }

    @Transactional
    public ProjectFeedbackItem updateProjectFeedback(Long registrationId,
                                                     ReviewStage stage,
                                                     ProjectFeedbackUpdateRequest request,
                                                     Long operatorId) {
        ensureFeedbackSupportedStage(stage);
        ProjectFeedback feedback = getOrCreateProjectFeedback(registrationId, stage, operatorId);
        feedback.setEditedHighlight(request.getHighlight());
        feedback.setEditedWeakness(request.getWeakness());
        feedback.setUpdatedById(operatorId);
        feedback.setUpdatedAt(LocalDateTime.now());
        return toProjectFeedbackItem(projectFeedbackRepository.save(feedback));
    }

    @Transactional
    public List<ProjectFeedbackItem> batchUpdateProjectFeedback(
            ReviewStage stage,
            List<com.trae.pinguan.web.dto.ProjectFeedbackBatchUpdateRequest.Item> items,
            Long operatorId) {
        ensureFeedbackSupportedStage(stage);

        List<Long> registrationIds = items.stream()
                .map(com.trae.pinguan.web.dto.ProjectFeedbackBatchUpdateRequest.Item::getRegistrationId)
                .collect(Collectors.toList());

        Map<Long, Registration> registrationMap = registrationRepository.findByIdInWithInstitution(registrationIds)
                .stream().collect(Collectors.toMap(Registration::getId, r -> r));

        Map<Long, ProjectFeedback> existingMap = projectFeedbackRepository
                .findByRegistrationIdInAndStage(registrationIds, stage)
                .stream().collect(Collectors.toMap(f -> f.getRegistration().getId(), f -> f));

        LocalDateTime now = LocalDateTime.now();
        List<ProjectFeedback> toSave = new ArrayList<>();

        for (com.trae.pinguan.web.dto.ProjectFeedbackBatchUpdateRequest.Item item : items) {
            Long regId = item.getRegistrationId();
            Registration registration = registrationMap.get(regId);
            if (registration == null) {
                throw new IllegalArgumentException("报名不存在: " + regId);
            }
            ProjectFeedback feedback = existingMap.getOrDefault(regId,
                    ProjectFeedback.builder()
                            .registration(registration)
                            .stage(stage)
                            .published(false)
                            .createdAt(now)
                            .build());
            feedback.setEditedHighlight(item.getHighlight());
            feedback.setEditedWeakness(item.getWeakness());
            feedback.setUpdatedById(operatorId);
            feedback.setUpdatedAt(now);
            toSave.add(feedback);
        }

        return projectFeedbackRepository.saveAll(toSave).stream()
                .map(this::toProjectFeedbackItem)
                .collect(Collectors.toList());
    }

    @Transactional
    public ProjectFeedbackItem publishProjectFeedback(Long registrationId,
                                                      ReviewStage stage,
                                                      boolean published,
                                                      Long operatorId) {
        ensureFeedbackSupportedStage(stage);
        ProjectFeedback feedback = getOrCreateProjectFeedback(registrationId, stage, operatorId);
        applyPublishState(feedback, published, operatorId);
        return toProjectFeedbackItem(projectFeedbackRepository.save(feedback));
    }

    @Transactional
    public List<ProjectFeedbackItem> publishProjectFeedbacks(Long competitionId,
                                                             ReviewStage stage,
                                                             boolean published,
                                                             Long operatorId) {
        ensureFeedbackSupportedStage(stage);
        List<ProjectFeedbackItem> refreshed = projectFeedbacksByStage(competitionId, stage);
        List<ProjectFeedback> feedbacks = projectFeedbackRepository
                .findByCompetitionIdAndStageWithRegistration(competitionId, stage);
        for (ProjectFeedback feedback : feedbacks) {
            applyPublishState(feedback, published, operatorId);
        }
        projectFeedbackRepository.saveAll(feedbacks);
        Map<Long, ProjectFeedback> savedByRegistrationId = feedbacks.stream()
                .collect(Collectors.toMap(f -> f.getRegistration().getId(), f -> f));
        return refreshed.stream()
                .map(item -> savedByRegistrationId.get(item.getRegistrationId()))
                .filter(java.util.Objects::nonNull)
                .sorted(Comparator.comparing((ProjectFeedback pf) -> pf.getRegistration().getId()))
                .map(this::toProjectFeedbackItem)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProjectFeedbackItem> publishedProjectFeedbacksByRegistration(Long registrationId, Long applicantId) {
        Registration registration = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        if (registration.getApplicant() == null || !registration.getApplicant().getId().equals(applicantId)) {
            throw new IllegalArgumentException("无权查看该项目反馈");
        }
        return projectFeedbackRepository.findByRegistrationIdAndPublishedTrueOrderByUpdatedAtDesc(registrationId)
                .stream()
                .map(this::toProjectFeedbackItem)
                .collect(Collectors.toList());
    }

    private ProjectFeedback getOrCreateProjectFeedback(Long registrationId, ReviewStage stage, Long operatorId) {
        Registration registration = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        List<ReviewTask> tasks = reviewTaskRepository.findByRegistrationIdAndStage(registrationId, stage);
        Map<Long, FeedbackSource> sourceMap = buildFeedbackSourceMap(tasks);
        FeedbackSource source = sourceMap.get(registrationId);
        LocalDateTime now = LocalDateTime.now();
        ProjectFeedback feedback = projectFeedbackRepository.findByRegistrationIdAndStage(registrationId, stage)
                .orElse(ProjectFeedback.builder()
                        .registration(registration)
                        .stage(stage)
                        .published(false)
                        .createdAt(now)
                        .build());
        feedback.setSourceHighlight(source != null ? source.joinHighlights() : null);
        feedback.setSourceWeakness(source != null ? source.joinWeaknesses() : null);
        feedback.setUpdatedById(operatorId);
        feedback.setUpdatedAt(now);
        return projectFeedbackRepository.save(feedback);
    }

    private List<ProjectFeedback> upsertProjectFeedbackSources(Map<Long, FeedbackSource> sourceMap,
                                                               ReviewStage stage,
                                                               Long operatorId) {
        if (sourceMap.isEmpty()) {
            return Collections.emptyList();
        }
        Set<Long> registrationIds = sourceMap.keySet();
        Map<Long, ProjectFeedback> existingMap = projectFeedbackRepository
                .findByRegistrationIdInAndStage(registrationIds, stage)
                .stream()
                .collect(Collectors.toMap(f -> f.getRegistration().getId(), f -> f));
        LocalDateTime now = LocalDateTime.now();
        List<ProjectFeedback> feedbacks = new ArrayList<>();
        for (FeedbackSource source : sourceMap.values()) {
            ProjectFeedback feedback = existingMap.get(source.registration.getId());
            if (feedback == null) {
                feedback = ProjectFeedback.builder()
                        .registration(source.registration)
                        .stage(stage)
                        .published(false)
                        .createdAt(now)
                        .build();
                feedback.setSourceHighlight(source.joinHighlights());
                feedback.setSourceWeakness(source.joinWeaknesses());
                feedback.setUpdatedById(operatorId);
                feedback.setUpdatedAt(now);
                feedbacks.add(feedback);
                continue;
            }
            String nextHighlight = source.joinHighlights();
            String nextWeakness = source.joinWeaknesses();
            boolean changed = !equalsNullable(feedback.getSourceHighlight(), nextHighlight)
                    || !equalsNullable(feedback.getSourceWeakness(), nextWeakness);
            if (changed) {
                feedback.setSourceHighlight(nextHighlight);
                feedback.setSourceWeakness(nextWeakness);
                feedback.setUpdatedById(operatorId);
                feedback.setUpdatedAt(now);
                feedbacks.add(feedback);
            }
        }
        if (feedbacks.isEmpty()) {
            return Collections.emptyList();
        }
        return projectFeedbackRepository.saveAll(feedbacks);
    }

    private Map<Long, FeedbackSource> buildFeedbackSourceMap(List<ReviewTask> tasks) {
        Set<Long> scoredTaskIds = tasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                .map(ReviewTask::getId)
                .collect(Collectors.toSet());
        Map<Long, ReviewScore> scoreMap = new HashMap<>();
        if (!scoredTaskIds.isEmpty()) {
            reviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                    .forEach(s -> scoreMap.put(s.getReviewTaskId(), s));
        }
        Map<Long, FeedbackSource> sourceMap = new java.util.LinkedHashMap<>();
        for (ReviewTask task : tasks) {
            Registration registration = task.getRegistration();
            if (registration == null) {
                continue;
            }
            FeedbackSource source = sourceMap.computeIfAbsent(
                    registration.getId(), id -> new FeedbackSource(registration));
            ReviewScore score = scoreMap.get(task.getId());
            if (task.getStatus() != ReviewStatus.SCORED || score == null) {
                continue;
            }
            addFeedbackLine(source.highlights, score.getHighlight());
            addFeedbackLine(source.weaknesses, score.getWeakness());
        }
        return sourceMap;
    }

    private void addFeedbackLine(List<String> target, String content) {
        if (content == null || content.trim().isEmpty()) {
            return;
        }
        target.add(content.trim());
    }

    private void applyPublishState(ProjectFeedback feedback, boolean published, Long operatorId) {
        feedback.setPublished(published);
        feedback.setPublishedById(published ? operatorId : null);
        feedback.setPublishedAt(published ? LocalDateTime.now() : null);
        feedback.setUpdatedById(operatorId);
        feedback.setUpdatedAt(LocalDateTime.now());
    }

    private ProjectFeedbackItem toProjectFeedbackItem(ProjectFeedback feedback) {
        Registration registration = feedback.getRegistration();
        String finalHighlight = feedback.getEditedHighlight() != null
                ? feedback.getEditedHighlight() : feedback.getSourceHighlight();
        String finalWeakness = feedback.getEditedWeakness() != null
                ? feedback.getEditedWeakness() : feedback.getSourceWeakness();
        return ProjectFeedbackItem.builder()
                .registrationId(registration != null ? registration.getId() : null)
                .projectName(registration != null ? registration.getProjectName() : null)
                .institutionName(registration != null && registration.getInstitution() != null
                        ? registration.getInstitution().getName() : null)
                .groupType(registration != null ? registration.getGroupType() : null)
                .groupCode(registration != null ? registration.getGroupCode() : null)
                .stage(feedback.getStage())
                .sourceHighlight(feedback.getSourceHighlight())
                .sourceWeakness(feedback.getSourceWeakness())
                .editedHighlight(feedback.getEditedHighlight())
                .editedWeakness(feedback.getEditedWeakness())
                .finalHighlight(finalHighlight)
                .finalWeakness(finalWeakness)
                .published(feedback.isPublished())
                .updatedAt(feedback.getUpdatedAt())
                .publishedAt(feedback.getPublishedAt())
                .build();
    }

    private void ensureFeedbackSupportedStage(ReviewStage stage) {
        if (stage != ReviewStage.BOOK) {
            throw new IllegalArgumentException("当前仅书审评分包含亮点与不足");
        }
    }

    private String normalize(String value) {
        if (value == null) {
            return null;
        }
        String trimmed = value.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }

    private boolean equalsNullable(String left, String right) {
        if (left == null) {
            return right == null;
        }
        return left.equals(right);
    }

    private static class FeedbackSource {
        private final Registration registration;
        private final List<String> highlights = new ArrayList<>();
        private final List<String> weaknesses = new ArrayList<>();

        private FeedbackSource(Registration registration) {
            this.registration = registration;
        }

        private String joinHighlights() {
            return String.join("\n", highlights);
        }

        private String joinWeaknesses() {
            return String.join("\n", weaknesses);
        }
    }

    @Transactional
    public ReviewScore submitScore(ReviewScoreRequest request) {
        ReviewTask task = reviewTaskRepository.findById(request.getReviewTaskId())
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        double total = request.getPlan() + request.getProblem() + request.getAction()
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
    public ReviewScore saveScoreDraft(com.trae.pinguan.web.dto.ReviewScoreDraftRequest request) {
        ReviewTask task = reviewTaskRepository.findById(request.getReviewTaskId())
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        if (task.getStatus() == ReviewStatus.SCORED) {
            throw new IllegalArgumentException("评分已正式提交，不可再修改草稿");
        }
        ReviewScore score = reviewScoreRepository.findByReviewTaskId(task.getId())
                .orElse(ReviewScore.builder().reviewTask(task).build());
        if (request.getPlan() != null)         score.setPlan(request.getPlan());
        if (request.getProblem() != null)      score.setProblem(request.getProblem());
        if (request.getAction() != null)       score.setAction(request.getAction());
        if (request.getSuccess() != null)      score.setSuccess(request.getSuccess());
        if (request.getReview() != null)       score.setReview(request.getReview());
        if (request.getOperation() != null)    score.setOperation(request.getOperation());
        if (request.getPresentation() != null) score.setPresentation(request.getPresentation());
        if (request.getHighlight() != null)    score.setHighlight(request.getHighlight());
        if (request.getWeakness() != null)     score.setWeakness(request.getWeakness());
        // 重新计算total（只有所有分项都有值时才计算）
        if (score.getPlan() != null && score.getProblem() != null && score.getAction() != null
                && score.getSuccess() != null && score.getReview() != null
                && score.getOperation() != null && score.getPresentation() != null) {
            score.setTotal(score.getPlan() + score.getProblem() + score.getAction()
                    + score.getSuccess() + score.getReview() + score.getOperation() + score.getPresentation());
        }
        ReviewScore saved = reviewScoreRepository.save(score);
        if (task.getStatus() == ReviewStatus.PENDING
                || task.getStatus() == ReviewStatus.CONFIRMED
                || task.getStatus() == ReviewStatus.RETURNED) {
            task.setStatus(ReviewStatus.DRAFT);
            task.setUpdatedAt(LocalDateTime.now());
            reviewTaskRepository.save(task);
        }
        return saved;
    }

    @Transactional
    public InterviewScore saveInterviewScoreDraft(com.trae.pinguan.web.dto.InterviewScoreDraftRequest request) {
        ReviewTask task = reviewTaskRepository.findById(request.getReviewTaskId())
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        if (task.getStatus() == ReviewStatus.SCORED) {
            throw new IllegalArgumentException("评分已正式提交，不可再修改草稿");
        }
        InterviewScore score = interviewScoreRepository.findByReviewTaskId(task.getId())
                .orElse(InterviewScore.builder().reviewTask(task).build());
        if (request.getTopic() != null)     score.setTopic(request.getTopic());
        if (request.getProcess() != null)   score.setProcess(request.getProcess());
        if (request.getOperation() != null) score.setOperation(request.getOperation());
        if (request.getResult() != null)    score.setResult(request.getResult());
        if (score.getTopic() != null && score.getProcess() != null
                && score.getOperation() != null && score.getResult() != null) {
            score.setTotal(score.getTopic() + score.getProcess() + score.getOperation() + score.getResult());
        }
        InterviewScore saved = interviewScoreRepository.save(score);
        if (task.getStatus() == ReviewStatus.PENDING
                || task.getStatus() == ReviewStatus.CONFIRMED
                || task.getStatus() == ReviewStatus.RETURNED) {
            task.setStatus(ReviewStatus.DRAFT);
            task.setUpdatedAt(LocalDateTime.now());
            reviewTaskRepository.save(task);
        }
        return saved;
    }

    @Transactional
    public ReviewTask recuseTask(Long taskId, com.trae.pinguan.web.dto.RecuseRequest request, Long reviewerId) {
        ReviewTask task = reviewTaskRepository.findById(taskId)
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        if (!task.getReviewer().getId().equals(reviewerId)) {
            throw new IllegalArgumentException("无权操作该任务");
        }
        if (task.getStatus() == ReviewStatus.SCORED) {
            throw new IllegalArgumentException("已提交评分，无法规避");
        }
        if (task.getStatus() == ReviewStatus.RECUSED) {
            throw new IllegalArgumentException("该任务已规避");
        }
        if ("OTHER".equals(request.getReasonCode()) &&
                (request.getReasonOther() == null || request.getReasonOther().trim().isEmpty())) {
            throw new IllegalArgumentException("选择\"其他\"时，请填写具体规避原因");
        }
        task.setStatus(ReviewStatus.RECUSED);
        task.setRecuseReasonCode(request.getReasonCode());
        task.setRecuseReasonOther(request.getReasonOther());
        task.setUpdatedAt(LocalDateTime.now());
        return reviewTaskRepository.save(task);
    }

    @Transactional
    public ReviewTask undoRecuseTask(Long taskId, Long reviewerId) {
        ReviewTask task = reviewTaskRepository.findById(taskId)
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        if (!task.getReviewer().getId().equals(reviewerId)) {
            throw new IllegalArgumentException("无权操作该任务");
        }
        if (task.getStatus() != ReviewStatus.RECUSED) {
            throw new IllegalArgumentException("该任务当前状态不是规避，无法撤销");
        }
        // 判断是否存在草稿分数：有草稿（submittedAt==null）→ DRAFT，否则 → PENDING
        ReviewStatus targetStatus = ReviewStatus.PENDING;
        if (task.getStage() == ReviewStage.BOOK) {
            Optional<ReviewScore> score = reviewScoreRepository.findByReviewTaskId(taskId);
            if (score.isPresent() && score.get().getSubmittedAt() == null) {
                targetStatus = ReviewStatus.DRAFT;
            }
        } else if (task.getStage() == ReviewStage.INTERVIEW) {
            Optional<InterviewScore> score = interviewScoreRepository.findByReviewTaskId(taskId);
            if (score.isPresent() && score.get().getSubmittedAt() == null) {
                targetStatus = ReviewStatus.DRAFT;
            }
        }
        task.setStatus(targetStatus);
        task.setRecuseReasonCode(null);
        task.setRecuseReasonOther(null);
        task.setUpdatedAt(LocalDateTime.now());
        return reviewTaskRepository.save(task);
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
        task.setStatus(ReviewStatus.RETURNED);
        return reviewTaskRepository.save(task);
    }

    @Transactional(readOnly = true)
    public List<ReviewSummaryItem> summaryByStage(Long competitionId, ReviewStage stage) {
        return summaryByStage(competitionId, stage, null);
    }

    public List<ReviewSummaryItem> summaryByStage(Long competitionId, ReviewStage stage, String reviewerName) {
        List<ReviewTask> tasks = reviewTaskRepository.findWithDetailsByStageAndCompetitionId(stage, competitionId);

        // 若指定评委姓名，只保留该评委承接的任务对应的项目（任意状态，只要有分配即可见）
        Set<Long> filteredRegIds = null;
        if (reviewerName != null && !reviewerName.trim().isEmpty()) {
            String name = reviewerName.trim();
            filteredRegIds = tasks.stream()
                    .filter(t -> t.getReviewer() != null
                            && name.equals(t.getReviewer().getName()))
                    .map(t -> t.getRegistration().getId())
                    .collect(Collectors.toSet());
        }
        final Set<Long> regIdFilter = filteredRegIds;

        Set<Long> scoredTaskIds = tasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                .map(ReviewTask::getId)
                .collect(Collectors.toSet());

        // 按阶段路由到正确的评分表
        Map<Long, Double> totalByTaskId = new HashMap<>();
        if (!scoredTaskIds.isEmpty()) {
            if (stage == ReviewStage.INTERVIEW) {
                interviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                        .forEach(s -> totalByTaskId.put(s.getReviewTaskId(), s.getTotal()));
            } else {
                reviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                        .forEach(s -> totalByTaskId.put(s.getReviewTaskId(), s.getTotal()));
            }
        }

        Map<Long, SummaryAccumulator> accumulators = new HashMap<>();
        for (ReviewTask task : tasks) {
            if (task.getStatus() != ReviewStatus.SCORED) continue;
            Double total = totalByTaskId.get(task.getId());
            if (total == null) continue;
            Long registrationId = task.getRegistration().getId();
            if (regIdFilter != null && !regIdFilter.contains(registrationId)) continue;
            SummaryAccumulator acc = accumulators.computeIfAbsent(registrationId, id -> new SummaryAccumulator(task));
            acc.add(total);
        }
        List<ReviewSummaryItem> result = new ArrayList<>();
        for (SummaryAccumulator acc : accumulators.values()) {
            result.add(new ReviewSummaryItem(
                    acc.registrationId,
                    acc.projectName,
                    acc.institutionName,
                    acc.groupType,
                    stage,
                    acc.avg(),
                    acc.count
            ));
        }
        return result;
    }

    @Transactional(readOnly = true)
    public List<ReviewRankingItem> rankingByStage(Long competitionId, ReviewStage stage, GroupType groupType) {
        List<ReviewSummaryItem> summary = summaryByStage(competitionId, stage);
        List<ReviewSummaryItem> filtered = summary.stream()
                .filter(item -> groupType == null || item.getGroupType() == groupType)
                .sorted(Comparator.comparing(ReviewSummaryItem::getAvgTotal).reversed())
                .collect(Collectors.toList());
        List<ReviewRankingItem> ranking = new ArrayList<>();
        int rank = 1;
        for (ReviewSummaryItem item : filtered) {
            ranking.add(ReviewRankingItem.builder()
                    .irank(rank++)
                    .registrationId(item.getRegistrationId())
                    .projectName(item.getProjectName())
                    .institutionName(item.getInstitutionName())
                    .groupType(item.getGroupType())
                    .stage(item.getStage())
                    .avgTotal(item.getAvgTotal())
                    .build());
        }
        return ranking;
    }

    // ─────────────────────────────────────────────────────────
    // 面谈评分
    // ─────────────────────────────────────────────────────────

    @Transactional
    public InterviewScore submitInterviewScore(InterviewScoreRequest request) {
        ReviewTask task = reviewTaskRepository.findById(request.getReviewTaskId())
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        if (task.getStage() != ReviewStage.INTERVIEW) {
            throw new IllegalArgumentException("该任务不属于面谈阶段");
        }
        double total = request.getTopic() + request.getProcess()
                + request.getOperation() + request.getResult();
        InterviewScore score = interviewScoreRepository.findByReviewTaskId(task.getId())
                .orElse(InterviewScore.builder().reviewTask(task).build());
        score.setTopic(request.getTopic());
        score.setProcess(request.getProcess());
        score.setOperation(request.getOperation());
        score.setResult(request.getResult());
        score.setTotal(total);
        score.setSubmittedAt(LocalDateTime.now());
        InterviewScore saved = interviewScoreRepository.save(score);
        task.setStatus(ReviewStatus.SCORED);
        task.setUpdatedAt(LocalDateTime.now());
        reviewTaskRepository.save(task);
        return saved;
    }

    @Transactional(readOnly = true)
    public Optional<InterviewScore> getInterviewScore(Long reviewTaskId) {
        return interviewScoreRepository.findByReviewTaskId(reviewTaskId);
    }

    @Transactional
    public void returnInterviewScore(Long reviewTaskId) {
        ReviewTask task = reviewTaskRepository.findById(reviewTaskId)
                .orElseThrow(() -> new IllegalArgumentException("评审任务不存在"));
        if (task.getStatus() != ReviewStatus.SCORED) {
            throw new IllegalArgumentException("评审未完成，无需退回");
        }
        String publishKey = "publish_" + task.getRegistration().getCompetition().getId()
                + "_" + task.getStage().name();
        boolean published = systemSettingRepository.findBySettingKey(publishKey)
                .map(s -> "true".equalsIgnoreCase(s.getSettingValue()))
                .orElse(false);
        if (published) {
            throw new IllegalArgumentException("已公布，无法退回");
        }
        task.setStatus(ReviewStatus.RETURNED);
        task.setUpdatedAt(LocalDateTime.now());
        reviewTaskRepository.save(task);
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> interviewSummaryByCompetition(Long competitionId) {
        List<ReviewTask> tasks = reviewTaskRepository.findWithDetailsByStageAndCompetitionId(
                ReviewStage.INTERVIEW, competitionId);
        Set<Long> scoredIds = tasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                .map(ReviewTask::getId)
                .collect(Collectors.toSet());
        Map<Long, InterviewScore> scoreMap = new HashMap<>();
        if (!scoredIds.isEmpty()) {
            interviewScoreRepository.findByReviewTaskIdIn(scoredIds)
                    .forEach(s -> scoreMap.put(s.getReviewTaskId(), s));
        }

        // 按 registrationId 聚合；面谈阶段仅统计进阶组
        Map<Long, Map<String, Object>> byReg = new java.util.LinkedHashMap<>();
        for (ReviewTask task : tasks) {
            if (task.getRegistration().getGroupType() != GroupType.ADVANCED) continue;
            Long regId = task.getRegistration().getId();
            Map<String, Object> item = byReg.computeIfAbsent(regId, id -> {
                Map<String, Object> m = new java.util.LinkedHashMap<>();
                m.put("registrationId", id);
                m.put("projectName", task.getRegistration().getProjectName());
                m.put("institutionName", task.getRegistration().getInstitution() != null
                        ? task.getRegistration().getInstitution().getName() : null);
                m.put("groupCode", task.getRegistration().getGroupCode());
                m.put("reviewerScores", new ArrayList<>());
                return m;
            });

            InterviewScore score = scoreMap.get(task.getId());
            Map<String, Object> reviewerScore = new HashMap<>();
            reviewerScore.put("reviewerId", task.getReviewer() != null ? task.getReviewer().getId() : null);
            reviewerScore.put("reviewerName", task.getReviewer() != null ? task.getReviewer().getName() : null);
            reviewerScore.put("status", task.getStatus().name());
            if (score != null) {
                reviewerScore.put("topic", score.getTopic());
                reviewerScore.put("process", score.getProcess());
                reviewerScore.put("operation", score.getOperation());
                reviewerScore.put("result", score.getResult());
                reviewerScore.put("total", score.getTotal());
            }
            ((List<Map<String, Object>>) item.get("reviewerScores")).add(reviewerScore);
        }

        // 计算每个项目的均分
        for (Map<String, Object> item : byReg.values()) {
            List<Map<String, Object>> scores = (List<Map<String, Object>>) item.get("reviewerScores");
            OptionalDouble avg = scores.stream()
                    .filter(s -> s.containsKey("total"))
                    .mapToDouble(s -> (Double) s.get("total"))
                    .average();
            item.put("avgTotal", avg.isPresent() ? avg.getAsDouble() : null);
        }
        return new ArrayList<>(byReg.values());
    }

    // ─────────────────────────────────────────────────────────
    // 系数调整排名计算（书审 / 面谈 / 决赛通用）
    // ─────────────────────────────────────────────────────────

    /**
     * 计算系数调整排名并持久化到 scoring_snapshots。
     * 逻辑：
     *   An = 小组内所有个人打分的均值（去除 <65 和 >95 的分数）
     *   B  = 全大组内所有个人打分的均值（去除 <65 和 >95 的分数）
     *   Cn = An / B（无效时取 1.0）
     *   D  = 项目原始均分 / Cn
     */
    @Transactional
    public List<ScoringSnapshot> computeAndSaveRanking(Long competitionId, ReviewStage stage, GroupType filterGroupType) {
        return computeAndSaveRanking(competitionId, stage, filterGroupType, false, null);
    }

    @Transactional
    public List<ScoringSnapshot> computeAndSaveRanking(Long competitionId, ReviewStage stage, GroupType filterGroupType, boolean interviewOnly) {
        return computeAndSaveRanking(competitionId, stage, filterGroupType, interviewOnly, null);
    }

    @Transactional
    public List<ScoringSnapshot> computeAndSaveRanking(Long competitionId, ReviewStage stage, GroupType filterGroupType, boolean interviewOnly, String jobId) {
        // interviewOnly=true 时，任务仍从 INTERVIEW 表读取，但快照写入 INTERVIEW_ONLY stage
        ReviewStage snapshotStage = (interviewOnly && stage == ReviewStage.INTERVIEW)
                ? ReviewStage.INTERVIEW_ONLY : stage;

        // 1. 取该赛事该阶段的所有任务（带关联数据，数据源始终是 INTERVIEW）
        reportProgress(jobId, 10, "正在加载评审任务…");
        List<ReviewTask> allTasks = reviewTaskRepository.findWithDetailsByStageAndCompetitionId(stage, competitionId);

        // 2. 获取各任务的原始分数（按阶段路由到对应表）
        reportProgress(jobId, 25, "正在读取原始评分…");
        Map<Long, Double> taskScores = getRawScoresByStage(stage, allTasks);

        // 3. 确定需要处理的 groupType 列表
        List<GroupType> groupTypes = filterGroupType != null
                ? Collections.singletonList(filterGroupType)
                : Arrays.asList(GroupType.values());

        // 4. 删除旧快照（按 snapshotStage 隔离，不影响另一路快照）
        reportProgress(jobId, 35, "正在清除旧快照…");
        if (filterGroupType != null) {
            scoringSnapshotRepository.deleteByCompetitionIdAndStageAndGroupType(competitionId, snapshotStage, filterGroupType);
        } else {
            scoringSnapshotRepository.deleteByCompetitionIdAndStage(competitionId, snapshotStage);
        }

        List<ScoringSnapshot> saved = new ArrayList<>();
        LocalDateTime now = LocalDateTime.now();

        int totalGroups = groupTypes.size();
        int groupIdx = 0;
        for (GroupType groupType : groupTypes) {
            groupIdx++;
            // 进度区间 40%~90%，按组数平均分配
            int pct = 40 + (groupIdx - 1) * 50 / totalGroups;
            reportProgress(jobId, pct, "正在计算 " + groupTypeLabel(groupType) + "（" + groupIdx + "/" + totalGroups + "）…");

            // 5a. 进阶组 + 面谈阶段：interviewOnly=false 时走书审合分逻辑；interviewOnly=true 时跳过，直接走通用路径
            if (groupType == GroupType.ADVANCED && stage == ReviewStage.INTERVIEW && !interviewOnly) {
                List<ScoringSnapshot> advSnaps = computeAdvancedCombinedRanking(
                        competitionId, allTasks, taskScores, now);
                saved.addAll(advSnaps);
                continue;
            }

            // 5. 过滤出该 groupType 的已打分任务
            List<ReviewTask> groupTypeTasks = allTasks.stream()
                    .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                    .filter(t -> t.getRegistration() != null
                            && t.getRegistration().getGroupType() == groupType)
                    .collect(Collectors.toList());
            if (groupTypeTasks.isEmpty()) {
                continue;
            }

            // 6. 计算全大组均分 B（去极值）
            // 综合组书审：B 按5个工具池分别计算，其他组/阶段统一用全量均值
            Map<String, Double> poolOverallAvgMap = new HashMap<>();
            double overallAvg;
            if (groupType == GroupType.COMPREHENSIVE && stage == ReviewStage.BOOK) {
                // 按工具池分组，分别计算各池 B 值
                Map<String, List<ReviewTask>> byPool = groupTypeTasks.stream()
                        .collect(Collectors.groupingBy(t ->
                                comprehensiveToolPool(t.getRegistration().getGroupCode())));
                for (Map.Entry<String, List<ReviewTask>> pe : byPool.entrySet()) {
                    List<Double> poolScores = pe.getValue().stream()
                            .map(t -> taskScores.get(t.getId()))
                            .filter(s -> s != null && s >= 65 && s <= 95)
                            .collect(Collectors.toList());
                    double poolB = poolScores.isEmpty() ? 0.0
                            : poolScores.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
                    poolOverallAvgMap.put(pe.getKey(), poolB);
                }
                // overallAvg 取全体综合组均值，仅作 fallback（正常不用）
                List<Double> allScoresForB = groupTypeTasks.stream()
                        .map(t -> taskScores.get(t.getId()))
                        .filter(s -> s != null && s >= 65 && s <= 95)
                        .collect(Collectors.toList());
                overallAvg = allScoresForB.isEmpty() ? 0.0
                        : allScoresForB.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            } else {
                List<Double> allScoresForB = groupTypeTasks.stream()
                        .map(t -> taskScores.get(t.getId()))
                        .filter(s -> s != null && s >= 65 && s <= 95)
                        .collect(Collectors.toList());
                overallAvg = allScoresForB.isEmpty() ? 0.0
                        : allScoresForB.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            }

            // 7. 按 groupCode 分组，计算各小组均分 An 及系数 Cn
            Map<String, List<ReviewTask>> byGroupCode = groupTypeTasks.stream()
                    .collect(Collectors.groupingBy(t -> {
                        String gc = t.getRegistration().getGroupCode();
                        return gc != null ? gc : "__NONE__";
                    }));
            Map<String, Double> groupCoefficients = new HashMap<>();
            Map<String, Double> groupAvgs = new HashMap<>();
            for (Map.Entry<String, List<ReviewTask>> entry : byGroupCode.entrySet()) {
                String gc = entry.getKey();
                // 综合组书审：用该小组所属工具池的 B；其他情况用全量 overallAvg
                double b = (groupType == GroupType.COMPREHENSIVE && stage == ReviewStage.BOOK)
                        ? poolOverallAvgMap.getOrDefault(comprehensiveToolPool(gc), overallAvg)
                        : overallAvg;
                List<Double> groupScores = entry.getValue().stream()
                        .map(t -> taskScores.get(t.getId()))
                        .filter(s -> s != null && s >= 65 && s <= 95)
                        .collect(Collectors.toList());
                double groupAvg = groupScores.isEmpty() ? b
                        : groupScores.stream().mapToDouble(Double::doubleValue).average().orElse(b);
                groupAvgs.put(gc, groupAvg);
                double cn = (b > 0) ? groupAvg / b : 1.0;
                groupCoefficients.put(gc, cn);
            }

            // 8. 按 registrationId 分组，计算项目原始均分和调整后分数
            Map<Long, List<ReviewTask>> byRegistration = groupTypeTasks.stream()
                    .collect(Collectors.groupingBy(t -> t.getRegistration().getId()));

            List<ScoringSnapshot> groupSnapshots = new ArrayList<>();
            for (Map.Entry<Long, List<ReviewTask>> entry : byRegistration.entrySet()) {
                Long registrationId = entry.getKey();
                List<ReviewTask> regTasks = entry.getValue();
                Registration reg = regTasks.get(0).getRegistration();

                List<Double> scores = regTasks.stream()
                        .map(t -> taskScores.get(t.getId()))
                        .filter(s -> s != null)
                        .collect(Collectors.toList());
                if (scores.isEmpty()) {
                    continue;
                }
                double rawAvg = scores.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);

                String gc = reg.getGroupCode() != null ? reg.getGroupCode() : "__NONE__";
                double cn = groupCoefficients.getOrDefault(gc, 1.0);
                double groupAvgVal = groupAvgs.getOrDefault(gc, overallAvg);
                double poolB = (groupType == GroupType.COMPREHENSIVE && stage == ReviewStage.BOOK)
                        ? poolOverallAvgMap.getOrDefault(comprehensiveToolPool(gc), overallAvg)
                        : overallAvg;
                double adjustedScore = cn > 0 ? rawAvg / cn : rawAvg;

                groupSnapshots.add(ScoringSnapshot.builder()
                        .competitionId(competitionId)
                        .registrationId(registrationId)
                        .stage(snapshotStage)
                        .groupCode(reg.getGroupCode())
                        .groupType(groupType)
                        .rawAvg(rawAvg)
                        .groupAvg(groupAvgVal)
                        .overallAvg(poolB)
                        .coefficient(cn)
                        .adjustedScore(adjustedScore)
                        .calculatedAt(now)
                        .build());
            }

            // 9. 按调整后分数降序排名
            groupSnapshots.sort(Comparator.comparing(ScoringSnapshot::getAdjustedScore).reversed());
            for (int i = 0; i < groupSnapshots.size(); i++) {
                groupSnapshots.get(i).setIrank(i + 1);
            }
            reportProgress(jobId, 40 + groupIdx * 50 / totalGroups, "正在写入 " + groupTypeLabel(groupType) + " 快照…");
            batchInsertSnapshots(groupSnapshots);
            saved.addAll(groupSnapshots);
        }
        reportProgress(jobId, 95, "快照写入完成，即将收尾…");
        return saved;
    }

    private void reportProgress(String jobId, int percent, String msg) {
        if (jobId != null) {
            computeJobTracker.progress(jobId, percent, msg);
        }
    }

    /**
     * 综合组书审：根据 groupCode 判断所属工具池（共5类）。
     * 工具池范围来源于《综合组分为5大组别》：
     *   B1–B3   十大安全目标
     *   B4–B9   问题解决型
     *   B10–B14 课题达成型及QFD
     *   B15–B19 PDCA循环
     *   B20–B22 综合工具
     */
    static String comprehensiveToolPool(String groupCode) {
        if (groupCode == null) return "UNKNOWN";
        // 提取数字部分，如 "B3" -> 3
        String numStr = groupCode.replaceAll("[^0-9]", "");
        if (numStr.isEmpty()) return "UNKNOWN";
        int n;
        try {
            n = Integer.parseInt(numStr);
        } catch (NumberFormatException e) {
            return "UNKNOWN";
        }
        if (n <= 3)  return "十大安全目标";
        if (n <= 9)  return "问题解决型";
        if (n <= 14) return "课题达成型及QFD";
        if (n <= 19) return "PDCA循环";
        if (n <= 22) return "综合工具";
        return "UNKNOWN";
    }

    private static String groupTypeLabel(GroupType gt) {
        if (gt == null) return "";
        switch (gt) {
            case BASIC:         return "基层组";
            case COMPREHENSIVE: return "综合组";
            case ADVANCED:      return "进阶组";
            default:            return gt.name();
        }
    }

    /**
     * 进阶组面谈阶段合分：书审调整分 × bookWeight + 面谈调整分 × interviewWeight。
     * 支持两种模式（系统设置 advanced_ranking_mode）：
     *   ADJUST_THEN_WEIGHT：各阶段分别系数调整后加权（默认）
     *   WEIGHT_THEN_ADJUST：先用原始分加权，再对加权分整体做系数调整
     */
    private List<ScoringSnapshot> computeAdvancedCombinedRanking(
            Long competitionId,
            List<ReviewTask> allInterviewTasks,
            Map<Long, Double> interviewTaskScores,
            LocalDateTime now) {

        double bookWeight = Double.parseDouble(
                systemSettingRepository.findBySettingKey("advanced_book_weight")
                        .map(s -> s.getSettingValue()).orElse("0.4"));
        double interviewWeight = Double.parseDouble(
                systemSettingRepository.findBySettingKey("advanced_interview_weight")
                        .map(s -> s.getSettingValue()).orElse("0.6"));
        String mode = systemSettingRepository.findBySettingKey("advanced_ranking_mode")
                .map(s -> s.getSettingValue()).orElse("ADJUST_THEN_WEIGHT");

        // 取进阶组面谈已打分任务
        List<ReviewTask> advTasks = allInterviewTasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                .filter(t -> t.getRegistration() != null
                        && t.getRegistration().getGroupType() == GroupType.ADVANCED)
                .collect(Collectors.toList());
        if (advTasks.isEmpty()) {
            return Collections.emptyList();
        }

        // 按项目分组，计算面谈原始均分
        Map<Long, List<ReviewTask>> byReg = advTasks.stream()
                .collect(Collectors.groupingBy(t -> t.getRegistration().getId()));

        Map<Long, Double> interviewRawAvg = new HashMap<>();
        Map<Long, Registration> regMap = new HashMap<>();
        for (Map.Entry<Long, List<ReviewTask>> e : byReg.entrySet()) {
            Registration reg = e.getValue().get(0).getRegistration();
            regMap.put(e.getKey(), reg);
            List<Double> scores = e.getValue().stream()
                    .map(t -> interviewTaskScores.get(t.getId()))
                    .filter(s -> s != null).collect(Collectors.toList());
            if (!scores.isEmpty()) {
                interviewRawAvg.put(e.getKey(), scores.stream()
                        .mapToDouble(Double::doubleValue).average().orElse(0));
            }
        }

        // 读书审快照（BOOK + ADVANCED）；bookWeight=0 时直接跳过，避免无谓查询
        Map<Long, Double> bookAdjusted = Collections.emptyMap();
        Map<Long, Double> bookRawAvgMap = Collections.emptyMap();
        if (bookWeight > 0) {
            List<ScoringSnapshot> bookSnaps = scoringSnapshotRepository
                    .findByCompetitionIdAndStageAndGroupTypeOrderByIrankAsc(
                            competitionId, ReviewStage.BOOK, GroupType.ADVANCED);
            bookAdjusted = bookSnaps.stream()
                    .filter(s -> s.getAdjustedScore() != null)
                    .collect(Collectors.toMap(ScoringSnapshot::getRegistrationId,
                            ScoringSnapshot::getAdjustedScore, (a, b) -> a));
            bookRawAvgMap = bookSnaps.stream()
                    .filter(s -> s.getRawAvg() != null)
                    .collect(Collectors.toMap(ScoringSnapshot::getRegistrationId,
                            ScoringSnapshot::getRawAvg, (a, b) -> a));
        }

        List<ScoringSnapshot> result = new ArrayList<>();

        if ("WEIGHT_THEN_ADJUST".equalsIgnoreCase(mode)) {
            // 先加权原始分，再整体系数调整（用面谈 groupCode）
            Map<Long, Double> combinedRaw = new HashMap<>();
            for (Long regId : interviewRawAvg.keySet()) {
                double iRaw = interviewRawAvg.get(regId);
                double bRaw = bookRawAvgMap.getOrDefault(regId, iRaw); // 若无书审数据则用面谈分
                combinedRaw.put(regId, bRaw * bookWeight + iRaw * interviewWeight);
            }

            // 全组均值 B（去极值 65~95，但合分可能超出范围，此处不去极值）
            double overallAvg = combinedRaw.values().stream()
                    .mapToDouble(Double::doubleValue).average().orElse(0);

            // 按面谈 groupCode 分小组均值 An
            Map<String, List<Long>> gcToRegs = new HashMap<>();
            for (Long regId : combinedRaw.keySet()) {
                String gc = Optional.ofNullable(regMap.get(regId))
                        .map(Registration::getGroupCode).orElse("__NONE__");
                gcToRegs.computeIfAbsent(gc, k -> new ArrayList<>()).add(regId);
            }
            Map<String, Double> gcAvg = new HashMap<>();
            for (Map.Entry<String, List<Long>> e : gcToRegs.entrySet()) {
                double avg = e.getValue().stream()
                        .mapToDouble(id -> combinedRaw.getOrDefault(id, 0.0))
                        .average().orElse(overallAvg);
                gcAvg.put(e.getKey(), avg);
            }

            for (Long regId : combinedRaw.keySet()) {
                Registration reg = regMap.get(regId);
                String gc = reg != null && reg.getGroupCode() != null
                        ? reg.getGroupCode() : "__NONE__";
                double an = gcAvg.getOrDefault(gc, overallAvg);
                double cn = overallAvg > 0 ? an / overallAvg : 1.0;
                double raw = combinedRaw.get(regId);
                double d = cn > 0 ? raw / cn : raw;
                result.add(ScoringSnapshot.builder()
                        .competitionId(competitionId)
                        .registrationId(regId)
                        .stage(ReviewStage.INTERVIEW)
                        .groupCode(reg != null ? reg.getGroupCode() : null)
                        .groupType(GroupType.ADVANCED)
                        .rawAvg(raw)           // 合权后的原始分
                        .groupAvg(an)
                        .overallAvg(overallAvg)
                        .coefficient(cn)
                        .adjustedScore(d)
                        .calculatedAt(now)
                        .build());
            }
        } else {
            // ADJUST_THEN_WEIGHT（默认）：各阶段分别系数调整后加权
            // 先算面谈的调整分（复用小组系数逻辑）
            List<Double> allInterviewScoresForB = advTasks.stream()
                    .map(t -> interviewTaskScores.get(t.getId()))
                    .filter(s -> s != null && s >= 65 && s <= 95)
                    .collect(Collectors.toList());
            double interviewOverallAvg = allInterviewScoresForB.isEmpty() ? 0
                    : allInterviewScoresForB.stream().mapToDouble(Double::doubleValue).average().orElse(0);

            Map<String, List<ReviewTask>> byGc = advTasks.stream()
                    .collect(Collectors.groupingBy(t -> {
                        String gc = t.getRegistration().getGroupCode();
                        return gc != null ? gc : "__NONE__";
                    }));
            Map<String, Double> gcCoeff = new HashMap<>();
            Map<String, Double> gcAvg   = new HashMap<>();
            for (Map.Entry<String, List<ReviewTask>> e : byGc.entrySet()) {
                List<Double> gs = e.getValue().stream()
                        .map(t -> interviewTaskScores.get(t.getId()))
                        .filter(s -> s != null && s >= 65 && s <= 95)
                        .collect(Collectors.toList());
                double an = gs.isEmpty() ? interviewOverallAvg
                        : gs.stream().mapToDouble(Double::doubleValue).average().orElse(interviewOverallAvg);
                gcAvg.put(e.getKey(), an);
                gcCoeff.put(e.getKey(), interviewOverallAvg > 0 ? an / interviewOverallAvg : 1.0);
            }

            for (Long regId : interviewRawAvg.keySet()) {
                Registration reg = regMap.get(regId);
                String gc = reg != null && reg.getGroupCode() != null
                        ? reg.getGroupCode() : "__NONE__";
                double iRaw = interviewRawAvg.get(regId);
                double cn   = gcCoeff.getOrDefault(gc, 1.0);
                double dInterview = cn > 0 ? iRaw / cn : iRaw;
                double dBook = bookAdjusted.getOrDefault(regId, iRaw); // 无书审快照则用面谈分替代
                double combined = dBook * bookWeight + dInterview * interviewWeight;

                result.add(ScoringSnapshot.builder()
                        .competitionId(competitionId)
                        .registrationId(regId)
                        .stage(ReviewStage.INTERVIEW)
                        .groupCode(reg != null ? reg.getGroupCode() : null)
                        .groupType(GroupType.ADVANCED)
                        .rawAvg(iRaw)                  // 面谈原始均分
                        .groupAvg(gcAvg.getOrDefault(gc, interviewOverallAvg))
                        .overallAvg(interviewOverallAvg)
                        .coefficient(cn)
                        .adjustedScore(combined)       // 最终合权分
                        .calculatedAt(now)
                        .build());
            }
        }

        // 按合权分降序排名
        result.sort(Comparator.comparing(ScoringSnapshot::getAdjustedScore).reversed());
        for (int i = 0; i < result.size(); i++) {
            result.get(i).setIrank(i + 1);
        }
        batchInsertSnapshots(result);
        return result;
    }

    /**
     * 按阶段路由取原始分数（taskId → total）。
     * 将来新增阶段只需在此方法中加一个 else-if 分支。
     */
    private Map<Long, Double> getRawScoresByStage(ReviewStage stage, List<ReviewTask> tasks) {
        Set<Long> scoredTaskIds = tasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                .map(ReviewTask::getId)
                .collect(Collectors.toSet());
        if (scoredTaskIds.isEmpty()) {
            return new HashMap<>();
        }
        Map<Long, Double> result = new HashMap<>();
        if (stage == ReviewStage.BOOK) {
            reviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                    .forEach(s -> result.put(s.getReviewTaskId(), s.getTotal()));
        } else if (stage == ReviewStage.INTERVIEW) {
            interviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                    .forEach(s -> result.put(s.getReviewTaskId(), s.getTotal()));
        }
        // FINAL: 待 final_scores 表设计完成后在此补充
        return result;
    }

    /**
     * 从快照读取排名列表（触发计算后调用）。
     */
    @Transactional(readOnly = true)
    public List<ReviewRankingItem> rankingFromSnapshot(Long competitionId, ReviewStage stage, GroupType groupType) {
        List<ScoringSnapshot> snapshots = groupType != null
                ? scoringSnapshotRepository.findByCompetitionIdAndStageAndGroupTypeOrderByIrankAsc(
                        competitionId, stage, groupType)
                : scoringSnapshotRepository.findByCompetitionIdAndStageOrderByIrankAsc(competitionId, stage);

        // 快照为空时直接返回空列表，引导前端先触发 compute-ranking
        if (snapshots.isEmpty()) {
            return Collections.emptyList();
        }

        // 批量加载项目名称、机构名称（LEFT JOIN FETCH institution，避免 N+1）
        Set<Long> regIds = snapshots.stream()
                .map(ScoringSnapshot::getRegistrationId)
                .collect(Collectors.toSet());
        Map<Long, Registration> regMap = registrationRepository.findByIdInWithInstitution(regIds).stream()
                .collect(Collectors.toMap(Registration::getId, r -> r));

        return snapshots.stream().map(s -> {
            Registration reg = regMap.get(s.getRegistrationId());
            return ReviewRankingItem.builder()
                    .irank(s.getIrank())
                    .registrationId(s.getRegistrationId())
                    .projectName(reg != null ? reg.getProjectName() : null)
                    .institutionName(reg != null && reg.getInstitution() != null
                            ? reg.getInstitution().getName() : null)
                    .groupType(s.getGroupType())
                    .groupCode(s.getGroupCode())
                    .stage(s.getStage())
                    .avgTotal(s.getRawAvg())
                    .groupAvg(s.getGroupAvg())
                    .overallAvg(s.getOverallAvg())
                    .coefficient(s.getCoefficient())
                    .adjustedScore(s.getAdjustedScore())
                    .calculatedAt(s.getCalculatedAt())
                    .build();
        }).collect(Collectors.toList());
    }

    private static class SummaryAccumulator {
        private final Long registrationId;
        private final String projectName;
        private final String institutionName;
        private final GroupType groupType;
        private int count;
        private double totalSum;

        private SummaryAccumulator(ReviewTask task) {
            this.registrationId = task.getRegistration().getId();
            this.projectName = task.getRegistration().getProjectName();
            this.institutionName = task.getRegistration().getInstitution().getName();
            this.groupType = task.getRegistration().getGroupType();
        }

        private void add(double total) {
            this.totalSum += total;
            this.count += 1;
        }

        private double avg() {
            if (count == 0) {
                return 0;
            }
            return totalSum / count;
        }
    }

    /**
     * 得分明细列表（书审 / 面谈通用）。
     * 每条记录对应一个参赛项目，嵌套每位评委的维度分和打分状态。
     */
    @Transactional(readOnly = true)
    public List<ScoreListItem> scoreListByStage(Long competitionId, ReviewStage stage,
            com.trae.pinguan.domain.enums.GroupType groupType,
            ReviewStatus reviewerStatus,
            String keyword,
            String reviewerName) {
        List<ReviewTask> tasks = reviewTaskRepository
                .findWithDetailsByStageAndCompetitionId(stage, competitionId);

        // 有评分记录的状态：DRAFT（草稿中）、SCORED（已提交）、RETURNED（已退回）
        Set<Long> withScoreTaskIds = tasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.DRAFT
                          || t.getStatus() == ReviewStatus.SCORED
                          || t.getStatus() == ReviewStatus.RETURNED)
                .map(ReviewTask::getId)
                .collect(Collectors.toSet());

        Map<Long, ReviewScore>    bookScoreMap = new HashMap<>();
        Map<Long, InterviewScore> intScoreMap  = new HashMap<>();
        if (!withScoreTaskIds.isEmpty()) {
            if (stage == ReviewStage.INTERVIEW) {
                interviewScoreRepository.findByReviewTaskIdIn(withScoreTaskIds)
                        .forEach(s -> intScoreMap.put(s.getReviewTaskId(), s));
            } else {
                reviewScoreRepository.findByReviewTaskIdIn(withScoreTaskIds)
                        .forEach(s -> bookScoreMap.put(s.getReviewTaskId(), s));
            }
        }

        // 展示所有非 CONFIRMED 任务（RECUSED 也展示，运营可见规避情况）；
        // 面谈阶段仅进阶组参与，保留原有过滤
        Map<Long, List<ReviewTask>> byReg = tasks.stream()
                .filter(t -> t.getStatus() != ReviewStatus.CONFIRMED)
                .filter(t -> stage != ReviewStage.INTERVIEW
                        || t.getRegistration().getGroupType() == GroupType.ADVANCED)
                .collect(Collectors.groupingBy(t -> t.getRegistration().getId()));

        // totalReviewers：该项目分配的总任务数
        Map<Long, Long> totalTaskCountByReg = tasks.stream()
                .collect(Collectors.groupingBy(
                        t -> t.getRegistration().getId(), Collectors.counting()));

        List<ScoreListItem> result = new ArrayList<>();
        for (Map.Entry<Long, List<ReviewTask>> entry : byReg.entrySet()) {
            Long regId = entry.getKey();
            List<ReviewTask> regTasks = entry.getValue();
            Registration reg = regTasks.get(0).getRegistration();

            List<ReviewerScoreDetail> reviewerScores = new ArrayList<>();
            double totalSum = 0;
            int scoredCount = 0;

            for (ReviewTask task : regTasks) {
                ReviewerScoreDetail.ReviewerScoreDetailBuilder b = ReviewerScoreDetail.builder()
                        .reviewTaskId(task.getId())
                        .reviewerId(task.getReviewer() != null ? task.getReviewer().getId() : null)
                        .reviewerName(task.getReviewer() != null ? task.getReviewer().getName() : null)
                        .status(task.getStatus().name());

                if (stage == ReviewStage.INTERVIEW) {
                    InterviewScore s = intScoreMap.get(task.getId());
                    if (s != null) {
                        b.topic(s.getTopic())
                         .process(s.getProcess())
                         .interviewOperation(s.getOperation())
                         .result(s.getResult())
                         .total(s.getTotal())
                         .submittedAt(s.getSubmittedAt());
                        // scoredCount / avgTotal 只统计正式提交（SCORED）
                        if (task.getStatus() == ReviewStatus.SCORED) {
                            totalSum += s.getTotal();
                            scoredCount++;
                        }
                    }
                } else {
                    ReviewScore s = bookScoreMap.get(task.getId());
                    if (s != null) {
                        b.plan(s.getPlan())
                         .problem(s.getProblem())
                         .action(s.getAction())
                         .success(s.getSuccess())
                         .review(s.getReview())
                         .operation(s.getOperation())
                         .presentation(s.getPresentation())
                         .total(s.getTotal())
                         .highlight(s.getHighlight())
                         .weakness(s.getWeakness())
                         .submittedAt(s.getSubmittedAt());
                        // scoredCount / avgTotal 只统计正式提交（SCORED）
                        if (task.getStatus() == ReviewStatus.SCORED) {
                            totalSum += s.getTotal();
                            scoredCount++;
                        }
                    }
                }
                reviewerScores.add(b.build());
            }

            // 评委排序固定按 reviewerId 升序，确保同专家在不同项目里位置一致
            reviewerScores.sort(java.util.Comparator.comparingLong(
                    rd -> rd.getReviewerId() != null ? rd.getReviewerId() : Long.MAX_VALUE));

            result.add(ScoreListItem.builder()
                    .registrationId(regId)
                    .finalSessionOrder(reg.getFinalSessionOrder())
                    .projectName(reg.getProjectName())
                    .institutionName(reg.getInstitution() != null ? reg.getInstitution().getName() : null)
                    .institutionLevel(reg.getInstitution() != null ? reg.getInstitution().getLevel() : null)
                    .groupType(reg.getGroupType())
                    .groupCode(reg.getGroupCode())
                    .stage(stage)
                    .reviewerScores(reviewerScores)
                    .scoredCount(scoredCount)
                    .totalReviewers(totalTaskCountByReg.getOrDefault(regId, 0L).intValue())
                    .avgTotal(scoredCount > 0 ? totalSum / scoredCount : null)
                    .build());
        }

        // ── 可选筛选（在内存中过滤，不影响其他逻辑）──────────────────────────

        // 1. 按组别过滤
        if (groupType != null) {
            result.removeIf(item -> item.getGroupType() != groupType);
        }

        // 2. 按评委打分状态过滤：只保留匹配状态的评委行，并重新计算 scoredCount/avgTotal
        if (reviewerStatus != null) {
            final String statusName = reviewerStatus.name();
            // 移除没有任何匹配评委行的项目
            result.removeIf(item -> item.getReviewerScores() == null
                    || item.getReviewerScores().stream().noneMatch(r -> statusName.equals(r.getStatus())));
            // 对保留的项目：只保留匹配的评委行，重算 scoredCount/avgTotal
            for (ScoreListItem item : result) {
                List<ReviewerScoreDetail> filtered = item.getReviewerScores().stream()
                        .filter(r -> statusName.equals(r.getStatus()))
                        .collect(Collectors.toList());
                item.setReviewerScores(filtered);
                // scoredCount / avgTotal 只统计 SCORED 状态
                int sc = 0;
                double sum = 0;
                for (ReviewerScoreDetail r : filtered) {
                    if (ReviewStatus.SCORED.name().equals(r.getStatus()) && r.getTotal() != null) {
                        sc++;
                        sum += r.getTotal();
                    }
                }
                item.setScoredCount(sc);
                item.setAvgTotal(sc > 0 ? sum / sc : null);
            }
        }

        // 3. 按项目名称或机构名称模糊搜索（不区分大小写）
        if (keyword != null && !keyword.trim().isEmpty()) {
            String kw = keyword.trim().toLowerCase();
            result.removeIf(item ->
                    (item.getProjectName() == null || !item.getProjectName().toLowerCase().contains(kw))
                 && (item.getInstitutionName() == null || !item.getInstitutionName().toLowerCase().contains(kw)));
        }

        // 4. 按评委姓名精准匹配：只保留该评委的行，并重新计算 scoredCount/avgTotal
        if (reviewerName != null && !reviewerName.trim().isEmpty()) {
            String name = reviewerName.trim();
            result.removeIf(item -> item.getReviewerScores() == null
                    || item.getReviewerScores().stream().noneMatch(r -> name.equals(r.getReviewerName())));
            for (ScoreListItem item : result) {
                List<ReviewerScoreDetail> filtered = item.getReviewerScores().stream()
                        .filter(r -> name.equals(r.getReviewerName()))
                        .collect(Collectors.toList());
                item.setReviewerScores(filtered);
                int sc = 0;
                double sum = 0;
                for (ReviewerScoreDetail r : filtered) {
                    if (ReviewStatus.SCORED.name().equals(r.getStatus()) && r.getTotal() != null) {
                        sc++;
                        sum += r.getTotal();
                    }
                }
                item.setScoredCount(sc);
                item.setAvgTotal(sc > 0 ? sum / sc : null);
            }
        }

        return result;
    }

    /**
     * 构造导出行数据：快照（排名/系数/调整分）+ 每位评委个人分。
     * 按 irank 升序排列，同组别内连续。
     */
    @Transactional(readOnly = true)
    public List<com.trae.pinguan.web.dto.ScoreExportRow> buildScoreExportRows(
            Long competitionId, ReviewStage stage) {

        List<ScoringSnapshot> snapshots = scoringSnapshotRepository
                .findByCompetitionIdAndStageOrderByIrankAsc(competitionId, stage);
        if (snapshots.isEmpty()) {
            return Collections.emptyList();
        }

        // 导出只需正式提交（SCORED）的评委个人分，独立查询不依赖 scoreListByStage
        // INTERVIEW_ONLY 快照的原始任务数据来源为 INTERVIEW stage
        ReviewStage taskStage = (stage == ReviewStage.INTERVIEW_ONLY) ? ReviewStage.INTERVIEW : stage;
        List<ReviewTask> allTasks = reviewTaskRepository
                .findWithDetailsByStageAndCompetitionId(taskStage, competitionId);
        Set<Long> scoredTaskIds = allTasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                .map(ReviewTask::getId)
                .collect(Collectors.toSet());
        // regId -> 按任务ID升序排列的 SCORED 任务列表（保持评委列顺序稳定）
        Map<Long, List<ReviewTask>> scoredByReg = allTasks.stream()
                .filter(t -> t.getStatus() == ReviewStatus.SCORED)
                .sorted(Comparator.comparingLong(ReviewTask::getId))
                .collect(Collectors.groupingBy(t -> t.getRegistration().getId()));
        // taskId -> total 分
        Map<Long, Double> taskTotalMap = new HashMap<>();
        if (!scoredTaskIds.isEmpty()) {
            if (taskStage == ReviewStage.INTERVIEW) {
                interviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                        .forEach(s -> taskTotalMap.put(s.getReviewTaskId(), s.getTotal()));
            } else {
                reviewScoreRepository.findByReviewTaskIdIn(scoredTaskIds)
                        .forEach(s -> taskTotalMap.put(s.getReviewTaskId(), s.getTotal()));
            }
        }

        // 报名基本信息
        Set<Long> regIds = snapshots.stream()
                .map(ScoringSnapshot::getRegistrationId).collect(Collectors.toSet());
        Map<Long, Registration> regMap = registrationRepository.findAllById(regIds).stream()
                .collect(Collectors.toMap(Registration::getId, r -> r));

        List<com.trae.pinguan.web.dto.ScoreExportRow> rows = new ArrayList<>();
        for (ScoringSnapshot snap : snapshots) {
            Long regId = snap.getRegistrationId();
            Registration reg = regMap.get(regId);

            List<Double> reviewerScores = new ArrayList<>();
            List<ReviewTask> regScoredTasks = scoredByReg.get(regId);
            if (regScoredTasks != null) {
                for (ReviewTask t : regScoredTasks) {
                    reviewerScores.add(taskTotalMap.get(t.getId()));
                }
            }

            rows.add(com.trae.pinguan.web.dto.ScoreExportRow.builder()
                    .irank(snap.getIrank())
                    .groupType(snap.getGroupType())
                    .groupCode(snap.getGroupCode())
                    .stage(stage)
                    .registrationId(regId)
                    .projectName(reg != null ? reg.getProjectName() : null)
                    .institutionName(reg != null && reg.getInstitution() != null
                            ? reg.getInstitution().getName() : null)
                    .reviewerScores(reviewerScores)
                    .rawAvg(snap.getRawAvg())
                    .groupAvg(snap.getGroupAvg())
                    .overallAvg(snap.getOverallAvg())
                    .coefficient(snap.getCoefficient())
                    .adjustedScore(snap.getAdjustedScore())
                    .build());
        }
        return rows;
    }

    /**
     * 原生 JDBC 批量 INSERT 快照，绕开 IDENTITY 主键限制，真正实现批量写库。
     * 不返回生成的 ID（调用方不需要），显著提升大数据量下的写入性能。
     */
    private void batchInsertSnapshots(List<ScoringSnapshot> snapshots) {
        if (snapshots.isEmpty()) return;
        String sql = "INSERT INTO scoring_snapshots " +
                "(competition_id, registration_id, stage, group_code, group_type, " +
                "raw_avg, group_avg, overall_avg, coefficient, adjusted_score, irank, calculated_at) " +
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)";
        jdbcTemplate.batchUpdate(sql, snapshots, 500, (ps, s) -> {
            ps.setLong(1, s.getCompetitionId());
            ps.setLong(2, s.getRegistrationId());
            ps.setString(3, s.getStage().name());
            ps.setString(4, s.getGroupCode());
            ps.setString(5, s.getGroupType().name());
            ps.setObject(6, s.getRawAvg());
            ps.setObject(7, s.getGroupAvg());
            ps.setObject(8, s.getOverallAvg());
            ps.setObject(9, s.getCoefficient());
            ps.setObject(10, s.getAdjustedScore());
            ps.setObject(11, s.getIrank());
            ps.setObject(12, s.getCalculatedAt() != null
                    ? Timestamp.valueOf(s.getCalculatedAt()) : null);
        });
    }
}
