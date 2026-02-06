package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.CompetitionTemplate;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CompetitionTemplateRepository extends JpaRepository<CompetitionTemplate, Long> {
    List<CompetitionTemplate> findByCompetitionId(Long competitionId);
}
