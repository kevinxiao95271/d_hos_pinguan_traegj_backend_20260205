package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.enums.CompetitionStage;
import com.trae.pinguan.repository.CompetitionRepository;
import com.trae.pinguan.web.dto.CompetitionCreateRequest;
import java.time.LocalDateTime;
import java.util.Comparator;
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
        return competitionRepository.findAll().stream()
                .max(Comparator.comparing(Competition::getId));
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
                .createdAt(LocalDateTime.now())
                .build();
        return competitionRepository.save(competition);
    }

    @Transactional
    public Competition updateStage(Long id, CompetitionStage stage) {
        Competition competition = competitionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        competition.setStage(stage);
        return competitionRepository.save(competition);
    }
}
