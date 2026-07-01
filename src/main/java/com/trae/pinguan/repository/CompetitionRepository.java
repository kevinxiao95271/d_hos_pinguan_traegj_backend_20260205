package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.enums.CompetitionStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface CompetitionRepository extends JpaRepository<Competition, Long> {
    java.util.Optional<Competition> findTop1ByOrderByIdDesc();

    boolean existsByNameAndIdNot(String name, Long id);

    boolean existsByName(String name);

    List<Competition> findByStatus(CompetitionStatus status);
}
