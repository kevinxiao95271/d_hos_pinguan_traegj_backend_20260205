package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.ActivityInfo;
import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.RegistrationMember;
import com.trae.pinguan.domain.entity.ReviewScore;
import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.repository.ActivityInfoRepository;
import com.trae.pinguan.repository.CompetitionRepository;
import com.trae.pinguan.repository.RegistrationMemberRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.repository.ReviewScoreRepository;
import com.trae.pinguan.repository.ReviewTaskRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.GroupTypeStatItem;
import com.trae.pinguan.web.dto.StatsSummaryResponse;
import java.util.ArrayList;
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

        // 一次性加载所有报名及其机构（JOIN FETCH，避免N次懒加载）
        List<Registration> registrations = registrationRepository.findByCompetitionIdWithInstitution(competitionId);
        // 报名机构去重总数
        long institutionCount = registrations.stream()
                .filter(r -> r.getInstitution() != null)
                .map(r -> r.getInstitution().getId())
                .distinct().count();
        Map<String, Integer> regionCounts = new HashMap<>();
        for (Registration registration : registrations) {
            String region = registration.getInstitution() != null ? registration.getInstitution().getRegion() : null;
            if (region == null || region.trim().isEmpty()) region = "未知";
            regionCounts.put(region, regionCounts.getOrDefault(region, 0) + 1);
        }

        // 批量加载所有ActivityInfo（1次查询），避免循环内N次单独查询
        List<Long> regIds = registrations.stream().map(Registration::getId).collect(Collectors.toList());
        Map<Long, ActivityInfo> activityMap = new HashMap<>();
        if (!regIds.isEmpty()) {
            activityInfoRepository.findByRegistrationIdIn(regIds)
                    .forEach(ai -> activityMap.put(ai.getRegistrationId(), ai));
        }

        // 收集所有需要翻译的code，批量查一次字典
        Set<String> codes = new HashSet<>();
        for (Registration registration : registrations) {
            ActivityInfo info = activityMap.get(registration.getId());
            if (info != null) {
                if (info.getSubjectTypeCode() != null && !info.getSubjectTypeCode().trim().isEmpty())
                    codes.add(info.getSubjectTypeCode());
                if (info.getMethodCode() != null && !info.getMethodCode().trim().isEmpty())
                    codes.add(info.getMethodCode());
            }
        }
        Map<String, String> labelMap = new HashMap<>();
        if (!codes.isEmpty()) {
            dictionaryItemRepository.findByCodes(codes)
                    .forEach(d -> labelMap.putIfAbsent(d.getCode(), d.getLabel()));
        }

        Set<String> toolTypes = new HashSet<>();
        Map<String, Integer> subjectTypeCounts = new HashMap<>();
        Map<String, Integer> methodCounts = new HashMap<>();
        for (Registration registration : registrations) {
            ActivityInfo info = activityMap.get(registration.getId());
            if (info != null && info.getMethodCode() != null) toolTypes.add(info.getMethodCode());

            String subjectTypeCode = info == null ? null : info.getSubjectTypeCode();
            String subjectLabel = (subjectTypeCode == null || subjectTypeCode.trim().isEmpty())
                    ? "未知" : labelMap.getOrDefault(subjectTypeCode, subjectTypeCode);
            subjectTypeCounts.put(subjectLabel, subjectTypeCounts.getOrDefault(subjectLabel, 0) + 1);

            String methodCode = info == null ? null : info.getMethodCode();
            String methodLabel = (methodCode == null || methodCode.trim().isEmpty())
                    ? "未知" : labelMap.getOrDefault(methodCode, methodCode);
            methodCounts.put(methodLabel, methodCounts.getOrDefault(methodLabel, 0) + 1);
        }

        // 批量加载所有成员（1次查询），按registrationId分组，避免N次单独查询
        Map<Long, List<RegistrationMember>> membersMap = new HashMap<>();
        if (!regIds.isEmpty()) {
            memberRepository.findByRegistrationIdIn(regIds)
                    .forEach(m -> membersMap.computeIfAbsent(m.getRegistrationId(), k -> new java.util.ArrayList<>()).add(m));
        }
        Map<String, Integer> leaderTitleCounts = new HashMap<>();
        for (Registration registration : registrations) {
            List<RegistrationMember> members = membersMap.getOrDefault(registration.getId(), java.util.Collections.emptyList());
            for (RegistrationMember member : members) {
                if (member.getRole() == com.trae.pinguan.domain.enums.MemberRole.PARTICIPANT) {
                    String title = member.getTitle();
                    if (title == null || title.trim().isEmpty()) title = "未知";
                    leaderTitleCounts.put(title, leaderTitleCounts.getOrDefault(title, 0) + 1);
                    break;
                }
            }
        }

        // 用 JOIN FETCH 一次性加载评委及其机构，避免N次懒加载
        List<UserAccount> reviewers = userAccountRepository.findByRoleWithInstitution(RoleType.REVIEWER);
        Set<Long> reviewerInstitutions = new HashSet<>();
        for (UserAccount reviewer : reviewers) {
            if (reviewer.getInstitution() != null) reviewerInstitutions.add(reviewer.getInstitution().getId());
        }

        List<ReviewTask> bookTasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(
                ReviewStage.BOOK, competitionId);
        Set<Long> bookTaskIds = new HashSet<>();
        for (ReviewTask task : bookTasks) bookTaskIds.add(task.getId());

        // 批量加载该赛事BOOK阶段的评分（避免findAll加载全量+N次懒加载getReviewTask()）
        Map<Long, ReviewScore> bookScores = new HashMap<>();
        if (!bookTaskIds.isEmpty()) {
            reviewScoreRepository.findByReviewTaskIdIn(bookTaskIds)
                    .forEach(score -> bookScores.put(score.getReviewTaskId(), score));
        }

        int scoredCount = bookScores.size();
        int unscoredCount = bookTaskIds.size() - scoredCount;

        double planSum = 0, problemSum = 0, actionSum = 0, successSum = 0,
               reviewSum = 0, operationSum = 0, presentationSum = 0;
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

        // 组别统计（利用已加载的registrations，institution已JOIN FETCH）
        int totalCount = registrations.size();
        Map<GroupType, Set<Long>> groupInstIds = new HashMap<>();
        Map<GroupType, Integer> groupProjCounts = new HashMap<>();
        for (GroupType gt : GroupType.values()) {
            groupInstIds.put(gt, new HashSet<>());
            groupProjCounts.put(gt, 0);
        }
        for (Registration reg : registrations) {
            GroupType gt = reg.getGroupType();
            if (gt == null) continue;
            groupProjCounts.put(gt, groupProjCounts.get(gt) + 1);
            if (reg.getInstitution() != null) groupInstIds.get(gt).add(reg.getInstitution().getId());
        }
        Map<GroupType, String> groupTypeNames = new HashMap<>();
        groupTypeNames.put(GroupType.BASIC, "基层组");
        groupTypeNames.put(GroupType.COMPREHENSIVE, "综合组");
        groupTypeNames.put(GroupType.ADVANCED, "进阶组");
        List<GroupTypeStatItem> groupTypeStats = new ArrayList<>();
        for (GroupType gt : GroupType.values()) {
            int projCount = groupProjCounts.get(gt);
            int instCount = groupInstIds.get(gt).size();
            double pct = totalCount == 0 ? 0.0 : Math.round(projCount * 1000.0 / totalCount) / 10.0;
            double avg = instCount == 0 ? 0.0 : Math.round(projCount * 100.0 / instCount) / 100.0;
            groupTypeStats.add(new GroupTypeStatItem(groupTypeNames.get(gt), instCount, projCount, pct, avg));
        }

        return new StatsSummaryResponse(
                competitionId,
                competition.getName(),
                registrations.size(),
                (int) institutionCount,
                toolTypes.size(),
                reviewers.size(),
                reviewerInstitutions.size(),
                bookTaskIds.size(),
                unscoredCount,
                regionCounts,
                subjectTypeCounts,
                methodCounts,
                leaderTitleCounts,
                groupTypeStats,
                planSum / divisor,
                problemSum / divisor,
                actionSum / divisor,
                successSum / divisor,
                reviewSum / divisor,
                operationSum / divisor,
                presentationSum / divisor
        );
    }
}
