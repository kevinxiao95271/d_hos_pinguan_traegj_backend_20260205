package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.enums.CompetitionStage;
import com.trae.pinguan.domain.enums.CompetitionStatus;
import com.trae.pinguan.exception.PrefixLockedByGroupingException;
import com.trae.pinguan.repository.CompetitionRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.web.dto.CompetitionConfigRequest;
import com.trae.pinguan.web.dto.CompetitionCreateRequest;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import com.trae.pinguan.repository.SystemSettingRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class CompetitionService {
    private final CompetitionRepository competitionRepository;
    private final RegistrationRepository registrationRepository;
    private final SystemSettingRepository systemSettingRepository;

    public List<Competition> listAll() {
        return competitionRepository.findAll();
    }

    public Competition get(Long id) {
        return competitionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
    }
    
    public Optional<Competition> getLatest() {
        return competitionRepository.findTop1ByOrderByIdDesc();
    }

    /**
     * 返回"当前赛事"：优先使用 OPS 通过 current-competition 接口设定的全局值；
     * 未设定时回退到 ID 最大的赛事。
     */
    public Optional<Competition> getCurrent() {
        Long systemCurrentId = systemSettingRepository.findBySettingKey("currentCompetitionId")
                .map(s -> { try { return Long.parseLong(s.getSettingValue()); } catch (Exception e) { return null; } })
                .orElse(null);
        if (systemCurrentId != null) {
            Optional<Competition> c = competitionRepository.findById(systemCurrentId);
            if (c.isPresent()) return c;
        }
        return competitionRepository.findTop1ByOrderByIdDesc();
    }

    /**
     * 返回当前赛事ID，找不到返回 null。
     */
    public Long getCurrentId() {
        return getCurrent().map(Competition::getId).orElse(null);
    }

    @Transactional
    public Competition create(CompetitionCreateRequest request) {
        if (competitionRepository.existsByName(request.getName())) {
            throw new IllegalArgumentException("赛事名称「" + request.getName() + "」已存在，请使用不同名称");
        }
        Competition competition = Competition.builder()
                .name(request.getName())
                .stage(CompetitionStage.REGISTER)
                .registerStart(request.getRegisterStart())
                .registerEnd(request.getRegisterEnd())
                .bookReviewStart(request.getBookReviewStart())
                .bookReviewEnd(request.getBookReviewEnd())
                .interviewStart(request.getInterviewStart())
                .interviewEnd(request.getInterviewEnd())
                .finalStart(request.getFinalStart())
                .finalEnd(request.getFinalEnd())
                .basicGroupPrefix(normalizePrefix(request.getBasicGroupPrefix(), "A"))
                .comprehensiveGroupPrefix(normalizePrefix(request.getComprehensiveGroupPrefix(), "B"))
                .advancedGroupPrefix(normalizePrefix(request.getAdvancedGroupPrefix(), "C"))
                .createdAt(LocalDateTime.now())
                .build();
        return competitionRepository.save(competition);
    }

    private String normalizePrefix(String raw, String defaultVal) {
        return (raw != null && !raw.trim().isEmpty()) ? raw.trim().toUpperCase() : defaultVal;
    }

    /** 激活赛事：同一业务年度只允许一个 ACTIVE */
    @Transactional
    public Competition activate(Long id) {
        Competition competition = competitionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        if (competition.getStatus() == CompetitionStatus.ACTIVE) {
            return competition;
        }
        int year = resolveCompetitionYear(competition);
        for (Competition other : competitionRepository.findByStatus(CompetitionStatus.ACTIVE)) {
            if (other.getId().equals(id)) {
                continue;
            }
            if (resolveCompetitionYear(other) == year) {
                throw new IllegalStateException(
                        year + " 年已存在激活赛事「" + other.getName() + "」，同一年度只允许一个 ACTIVE 赛事");
            }
        }
        competition.setStatus(CompetitionStatus.ACTIVE);
        return competitionRepository.save(competition);
    }

    /**
     * 赛事业务年度：优先取报名开始时间的年份，否则取创建时间年份。
     * 避免 2026 年底创建「2027 届」赛事时被误判为 2026 年。
     */
    int resolveCompetitionYear(Competition competition) {
        if (competition.getRegisterStart() != null) {
            return competition.getRegisterStart().getYear();
        }
        if (competition.getCreatedAt() != null) {
            return competition.getCreatedAt().getYear();
        }
        return LocalDateTime.now().getYear();
    }

    /** 撤回激活：仅限无报名记录时可将 ACTIVE 改回 DRAFT */
    @Transactional
    public Competition deactivate(Long id) {
        Competition competition = competitionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        if (competition.getStatus() != CompetitionStatus.ACTIVE) {
            return competition;
        }
        long regCount = registrationRepository.countByCompetitionId(id);
        if (regCount > 0) {
            throw new IllegalStateException("该赛事已有 " + regCount + " 条报名记录，不可撤回激活");
        }
        competition.setStatus(CompetitionStatus.DRAFT);
        return competitionRepository.save(competition);
    }

    /** 删除赛事：仅限 DRAFT 且无任何报名记录 */
    @Transactional
    public void delete(Long id) {
        Competition competition = competitionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        if (competition.getStatus() == CompetitionStatus.ACTIVE) {
            throw new IllegalStateException("ACTIVE 赛事不可删除，请先撤回激活");
        }
        long regCount = registrationRepository.countByCompetitionId(id);
        if (regCount > 0) {
            throw new IllegalStateException("该赛事已有 " + regCount + " 条报名记录，不可删除");
        }
        competitionRepository.deleteById(id);
    }

    @Transactional
    public Competition updateStage(Long id, CompetitionStage stage) {
        Competition competition = competitionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        competition.setStage(stage);
        return competitionRepository.save(competition);
    }

    @Transactional
    public Competition updateConfig(Long id, CompetitionConfigRequest req) {
        Competition competition = competitionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        boolean isActive = competition.getStatus() == CompetitionStatus.ACTIVE;

        // 名称和分组前缀在 ACTIVE 后锁定
        if (req.getName() != null && !req.getName().trim().isEmpty()) {
            if (isActive) {
                throw new IllegalStateException("赛事已激活，名称不可修改");
            }
            String newName = req.getName().trim();
            if (competitionRepository.existsByNameAndIdNot(newName, id)) {
                throw new IllegalArgumentException("赛事名称「" + newName + "」已存在，请使用不同名称");
            }
            competition.setName(newName);
        }

        // 阶段和时间窗口 ACTIVE 后仍可调整
        if (req.getStage()           != null) competition.setStage(req.getStage());
        if (req.getRegisterStart()   != null) competition.setRegisterStart(req.getRegisterStart());
        if (req.getRegisterEnd()     != null) competition.setRegisterEnd(req.getRegisterEnd());
        if (req.getBookReviewStart() != null) competition.setBookReviewStart(req.getBookReviewStart());
        if (req.getBookReviewEnd()   != null) competition.setBookReviewEnd(req.getBookReviewEnd());
        if (req.getInterviewStart()  != null) competition.setInterviewStart(req.getInterviewStart());
        if (req.getInterviewEnd()    != null) competition.setInterviewEnd(req.getInterviewEnd());
        if (req.getFinalStart()      != null) competition.setFinalStart(req.getFinalStart());
        if (req.getFinalEnd()        != null) competition.setFinalEnd(req.getFinalEnd());

        boolean wantChangePrefix = req.getBasicGroupPrefix() != null
                || req.getComprehensiveGroupPrefix() != null
                || req.getAdvancedGroupPrefix() != null;
        if (wantChangePrefix) {
            if (isActive) {
                throw new IllegalStateException("赛事已激活，分组前缀不可修改");
            }
            if (registrationRepository.existsGroupedByCompetitionId(id)) {
                throw new PrefixLockedByGroupingException(id);
            }
        }
        if (req.getBasicGroupPrefix()         != null) competition.setBasicGroupPrefix(req.getBasicGroupPrefix().trim().toUpperCase());
        if (req.getComprehensiveGroupPrefix() != null) competition.setComprehensiveGroupPrefix(req.getComprehensiveGroupPrefix().trim().toUpperCase());
        if (req.getAdvancedGroupPrefix()      != null) competition.setAdvancedGroupPrefix(req.getAdvancedGroupPrefix().trim().toUpperCase());
        return competitionRepository.save(competition);
    }
}
