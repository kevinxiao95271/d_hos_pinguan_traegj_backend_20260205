package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.enums.CompetitionStage;
import com.trae.pinguan.repository.CompetitionRepository;
import com.trae.pinguan.web.dto.CompetitionConfigRequest;
import com.trae.pinguan.web.dto.CompetitionCreateRequest;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class CompetitionService {
    private final CompetitionRepository competitionRepository;

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

    @Transactional
    public Competition create(CompetitionCreateRequest request) {
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
        if (req.getStage()           != null) competition.setStage(req.getStage());
        if (req.getRegisterStart()   != null) competition.setRegisterStart(req.getRegisterStart());
        if (req.getRegisterEnd()     != null) competition.setRegisterEnd(req.getRegisterEnd());
        if (req.getBookReviewStart() != null) competition.setBookReviewStart(req.getBookReviewStart());
        if (req.getBookReviewEnd()   != null) competition.setBookReviewEnd(req.getBookReviewEnd());
        if (req.getInterviewStart()  != null) competition.setInterviewStart(req.getInterviewStart());
        if (req.getInterviewEnd()    != null) competition.setInterviewEnd(req.getInterviewEnd());
        if (req.getFinalStart()      != null) competition.setFinalStart(req.getFinalStart());
        if (req.getFinalEnd()        != null) competition.setFinalEnd(req.getFinalEnd());
        if (req.getBasicGroupPrefix()         != null) competition.setBasicGroupPrefix(req.getBasicGroupPrefix().trim().toUpperCase());
        if (req.getComprehensiveGroupPrefix() != null) competition.setComprehensiveGroupPrefix(req.getComprehensiveGroupPrefix().trim().toUpperCase());
        if (req.getAdvancedGroupPrefix()      != null) competition.setAdvancedGroupPrefix(req.getAdvancedGroupPrefix().trim().toUpperCase());
        return competitionRepository.save(competition);
    }
}
