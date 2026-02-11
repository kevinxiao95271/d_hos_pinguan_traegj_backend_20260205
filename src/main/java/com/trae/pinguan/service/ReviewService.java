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

    public List<ReviewTask> listTasksByStage(Long competitionId, ReviewStage stage, ReviewStatus status) {
        if (status == null) {
            return reviewTaskRepository.findByStageAndRegistrationCompetitionId(stage, competitionId);
        }
        return reviewTaskRepository.findByStageAndStatusAndRegistrationCompetitionId(stage, status, competitionId);
    }

    @Transactional(readOnly = true)
    public List<com.trae.pinguan.web.dto.AdminReviewTaskItem> listTasksForAdmin(Long competitionId, ReviewStage stage, ReviewStatus status) {
        List<ReviewTask> tasks;
        
        if (stage == null && status == null) {
            // 查询所有任务
            tasks = reviewTaskRepository.findByRegistrationCompetitionId(competitionId);
        } else if (stage == null) {
            // 只按status筛选
            tasks = reviewTaskRepository.findByStatusAndRegistrationCompetitionId(status, competitionId);
        } else if (status == null) {
            // 只按stage筛选
            tasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(stage, competitionId);
        } else {
            // 同时按stage和status筛选
            tasks = reviewTaskRepository.findByStageAndStatusAndRegistrationCompetitionId(stage, status, competitionId);
        }
        
        return tasks.stream()
                .map(task -> {
                    Registration reg = task.getRegistration();
                    UserAccount reviewer = task.getReviewer();
                    
                    return com.trae.pinguan.web.dto.AdminReviewTaskItem.builder()
                            .id(task.getId())
                            .stage(task.getStage())
                            .status(task.getStatus())
                            .createdAt(task.getCreatedAt())
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
            
            // 删除分组匹配逻辑 - 评审专家可以评审任何分组的项目
            // 评审专家的分配主要基于expertBackground（专业背景）
            
            // 避免同机构评审
            if (reviewer.getInstitution() != null && registration.getInstitution() != null
                    && reviewer.getInstitution().getId().equals(registration.getInstitution().getId())) {
                continue;
            }
            
            // 避免重复分配
            if (assignedReviewerIds.contains(reviewer.getId())) {
                continue;
            }
            
            // 确保不同专业背景（如果需要）
            if (requireDifferentBackground && reviewer.getExpertBackground() != null && assignedBackgrounds.size() == 1) {
                if (assignedBackgrounds.contains(reviewer.getExpertBackground())) {
                    continue;
                }
            }
            
            // 检查负荷上限
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
            ranking.add(new ReviewRankingItem(
                    rank++,
                    item.getRegistrationId(),
                    item.getProjectName(),
                    item.getInstitutionName(),
                    item.getGroupType(),
                    item.getStage(),
                    item.getAvgTotal()
            ));
        }
        return ranking;
    }

    @Transactional(readOnly = true)
    public List<com.trae.pinguan.web.dto.BookScoreItem> listBookScores(
            Long competitionId,
            ReviewStatus status,
            Long reviewerId,
            Long institutionId,
            GroupType groupType) {
        
        List<ReviewTask> tasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(
                ReviewStage.BOOK, competitionId);
        
        List<com.trae.pinguan.web.dto.BookScoreItem> result = new ArrayList<>();
        
        for (ReviewTask task : tasks) {
            // 筛选条件
            if (status != null && task.getStatus() != status) {
                continue;
            }
            if (reviewerId != null && (task.getReviewer() == null || !task.getReviewer().getId().equals(reviewerId))) {
                continue;
            }
            // 删除reviewerGroupCode筛选 - 评审专家没有分组限制
            if (institutionId != null && (task.getRegistration().getInstitution() == null 
                    || !task.getRegistration().getInstitution().getId().equals(institutionId))) {
                continue;
            }
            if (groupType != null && task.getRegistration().getGroupType() != groupType) {
                continue;
            }
            
            // 只返回已评分的任务
            if (task.getStatus() != ReviewStatus.SCORED) {
                continue;
            }
            
            // 获取评分详情
            ReviewScore score = reviewScoreRepository.findByReviewTaskId(task.getId()).orElse(null);
            if (score == null) {
                continue;
            }
            
            // 构建返回对象
            com.trae.pinguan.web.dto.BookScoreItem item = com.trae.pinguan.web.dto.BookScoreItem.builder()
                    .taskId(task.getId())
                    .status(task.getStatus())
                    .createdAt(task.getCreatedAt())
                    .registrationId(task.getRegistration().getId())
                    .projectName(task.getRegistration().getProjectName())
                    .institutionName(task.getRegistration().getInstitution() != null 
                            ? task.getRegistration().getInstitution().getName() : null)
                    .institutionLevel(task.getRegistration().getInstitution() != null 
                            ? task.getRegistration().getInstitution().getLevel() : null)
                    .groupType(task.getRegistration().getGroupType())
                    .groupCode(task.getRegistration().getGroupCode())
                    .reviewerId(task.getReviewer() != null ? task.getReviewer().getId() : null)
                    .reviewerName(task.getReviewer() != null ? task.getReviewer().getName() : null)
                    .reviewerTitle(task.getReviewer() != null ? task.getReviewer().getTitle() : null)
                    .reviewerInstitutionName(task.getReviewer() != null && task.getReviewer().getInstitution() != null 
                            ? task.getReviewer().getInstitution().getName() : null)
                    .scoreId(score.getId())
                    .plan(score.getPlan())
                    .problem(score.getProblem())
                    .action(score.getAction())
                    .success(score.getSuccess())
                    .review(score.getReview())
                    .operation(score.getOperation())
                    .presentation(score.getPresentation())
                    .total(score.getTotal())
                    .submittedAt(score.getSubmittedAt())
                    .build();
            
            result.add(item);
        }
        
        // 按提交时间降序排列
        result.sort(Comparator.comparing(com.trae.pinguan.web.dto.BookScoreItem::getSubmittedAt).reversed());
        
        return result;
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
}
