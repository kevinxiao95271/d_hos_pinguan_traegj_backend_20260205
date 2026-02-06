package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.repository.CompetitionRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.web.dto.CompetitionMergeRequest;
import com.trae.pinguan.web.dto.CompetitionMergeResponse;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class CompetitionMaintenanceService {
    private final CompetitionRepository competitionRepository;
    private final RegistrationRepository registrationRepository;

    @Transactional
    public CompetitionMergeResponse mergeCompetitions(CompetitionMergeRequest request) {
        Competition target = competitionRepository.findById(request.getTargetCompetitionId())
                .orElseThrow(() -> new IllegalArgumentException("目标赛事不存在"));
        Set<Long> keepIds = new HashSet<>(request.getKeepCompetitionIds());
        keepIds.add(target.getId());
        List<Competition> all = competitionRepository.findAll();
        List<Long> removedIds = new ArrayList<>();
        int moved = 0;
        boolean moveAll = request.getMoveAllRegistrationsToTarget() == null || request.getMoveAllRegistrationsToTarget();

        for (Competition competition : all) {
            if (competition.getId().equals(target.getId())) {
                continue;
            }
            List<Registration> registrations = registrationRepository.findByCompetitionId(competition.getId());
            if (moveAll || !keepIds.contains(competition.getId())) {
                for (Registration registration : registrations) {
                    registration.setCompetition(target);
                }
                registrationRepository.saveAll(registrations);
                moved += registrations.size();
            }
        }

        for (Competition competition : all) {
            if (keepIds.contains(competition.getId())) {
                continue;
            }
            competitionRepository.deleteById(competition.getId());
            removedIds.add(competition.getId());
        }

        return new CompetitionMergeResponse(target.getId(), new ArrayList<>(keepIds), removedIds, moved);
    }
}
