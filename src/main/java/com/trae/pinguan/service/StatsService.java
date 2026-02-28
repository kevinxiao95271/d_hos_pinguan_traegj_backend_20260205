package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.ActivityInfo;
import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.RegistrationMember;
import com.trae.pinguan.domain.entity.ReviewScore;
import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.repository.ActivityInfoRepository;
import com.trae.pinguan.repository.CompetitionRepository;
import com.trae.pinguan.repository.RegistrationMemberRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.repository.ReviewScoreRepository;
import com.trae.pinguan.repository.ReviewTaskRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.StatsSummaryResponse;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class StatsService {
    private final CompetitionRepository competitionRepository;
    private final RegistrationRepository registrationRepository;
    private final ActivityInfoRepository activityInfoRepository;
    private final ReviewTaskRepository reviewTaskRepository;
    private final ReviewScoreRepository reviewScoreRepository;
    private final UserAccountRepository userAccountRepository;
    private final RegistrationMemberRepository memberRepository;
    private final com.trae.pinguan.repository.DictionaryItemRepository dictionaryItemRepository;

    @Transactional(readOnly = true)
    public StatsSummaryResponse summaryForLatestCompetition() {
        Competition competition = competitionRepository.findAll().stream()
                .max(Comparator.comparing(Competition::getId))
                .orElseThrow(() -> new IllegalArgumentException("暂无赛事"));
        return summaryForCompetition(competition.getId());
    }

    @Transactional(readOnly = true)
    public StatsSummaryResponse summaryForCompetition(Long competitionId) {
        Competition competition = competitionRepository.findById(competitionId)
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));

        List<Registration> registrations = registrationRepository.findByCompetitionId(competitionId);
        Map<String, Integer> regionCounts = new HashMap<>();
        for (Registration registration : registrations) {
            String region = null;
            if (registration.getInstitution() != null) {
                region = registration.getInstitution().getRegion();
            }
            if (region == null || region.trim().isEmpty()) {
                region = "未知";
            }
            regionCounts.put(region, regionCounts.getOrDefault(region, 0) + 1);
        }

        Set<String> toolTypes = new HashSet<>();
        Map<String, Integer> subjectTypeCounts = new HashMap<>();
        Map<String, Integer> methodCounts = new HashMap<>();
        
        for (Registration registration : registrations) {
            ActivityInfo info = activityInfoRepository.findByRegistrationId(registration.getId()).orElse(null);
            if (info != null && info.getMethodCode() != null) {
                toolTypes.add(info.getMethodCode());
            }
            String subjectTypeCode = info == null ? null : info.getSubjectTypeCode();
            if (subjectTypeCode == null || subjectTypeCode.trim().isEmpty()) {
                subjectTypeCounts.put("未知", subjectTypeCounts.getOrDefault("未知", 0) + 1);
            } else {
                // 将code转换为label
                String label = getLabel(subjectTypeCode);
                subjectTypeCounts.put(label, subjectTypeCounts.getOrDefault(label, 0) + 1);
            }
            
            // 统计品管工具分布
            String methodCode = info == null ? null : info.getMethodCode();
            if (methodCode == null || methodCode.trim().isEmpty()) {
                methodCounts.put("未知", methodCounts.getOrDefault("未知", 0) + 1);
            } else {
                // 将code转换为label
                String label = getLabel(methodCode);
                methodCounts.put(label, methodCounts.getOrDefault(label, 0) + 1);
            }
        }

        // 统计项目负责人职称分布
        Map<String, Integer> leaderTitleCounts = new HashMap<>();
        for (Registration registration : registrations) {
            List<RegistrationMember> members = memberRepository.findByRegistrationId(registration.getId());
            for (RegistrationMember member : members) {
                if (member.getRole() == com.trae.pinguan.domain.enums.MemberRole.PARTICIPANT) {
                    String title = member.getTitle();
                    if (title == null || title.trim().isEmpty()) {
                        title = "未知";
                    }
                    leaderTitleCounts.put(title, leaderTitleCounts.getOrDefault(title, 0) + 1);
                    break;  // 每个项目只统计一个负责人
                }
            }
        }

        List<UserAccount> reviewers = userAccountRepository.findAll().stream()
                .filter(user -> user.getRole() == RoleType.REVIEWER)
                .collect(Collectors.toList());
        Set<Long> reviewerInstitutions = new HashSet<>();
        for (UserAccount reviewer : reviewers) {
            if (reviewer.getInstitution() != null) {
                reviewerInstitutions.add(reviewer.getInstitution().getId());
            }
        }

        List<ReviewTask> bookTasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(
                ReviewStage.BOOK, competitionId);
        Set<Long> bookTaskIds = new HashSet<>();
        for (ReviewTask task : bookTasks) {
            bookTaskIds.add(task.getId());
        }

        List<ReviewScore> allScores = reviewScoreRepository.findAll();
        Map<Long, ReviewScore> bookScores = new HashMap<>();
        for (ReviewScore score : allScores) {
            ReviewTask task = score.getReviewTask();
            if (task != null && bookTaskIds.contains(task.getId())) {
                bookScores.put(task.getId(), score);
            }
        }

        int scoredCount = bookScores.size();
        int unscoredCount = bookTaskIds.size() - scoredCount;

        double planSum = 0;
        double problemSum = 0;
        double actionSum = 0;
        double successSum = 0;
        double reviewSum = 0;
        double operationSum = 0;
        double presentationSum = 0;
        for (ReviewScore score : bookScores.values()) {
            planSum += score.getPlan();
            problemSum += score.getProblem();
            actionSum += score.getAction();
            successSum += score.getSuccess();
            reviewSum += score.getReview();
            operationSum += score.getOperation();
            presentationSum += score.getPresentation();
        }

        double divisor = scoredCount == 0 ? 1 : scoredCount;

        return new StatsSummaryResponse(
                competitionId,
                competition.getName(),
                registrations.size(),
                toolTypes.size(),
                reviewers.size(),
                reviewerInstitutions.size(),
                bookTaskIds.size(),
                unscoredCount,
                regionCounts,
                subjectTypeCounts,
                methodCounts,
                leaderTitleCounts,
                planSum / divisor,
                problemSum / divisor,
                actionSum / divisor,
                successSum / divisor,
                reviewSum / divisor,
                operationSum / divisor,
                presentationSum / divisor
        );
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
}
