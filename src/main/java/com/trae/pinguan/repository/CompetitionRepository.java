package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.enums.CompetitionStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;

public interface CompetitionRepository extends JpaRepository<Competition, Long> {
    java.util.Optional<Competition> findTop1ByOrderByIdDesc();

    /** 查同年同状态的赛事（用于同年 ACTIVE 唯一性校验） */
    @Query("SELECT c FROM Competition c WHERE c.status = :status AND YEAR(c.createdAt) = :year AND c.id <> :excludeId")
    List<Competition> findByStatusAndYearExcluding(
            @Param("status") CompetitionStatus status,
            @Param("year") int year,
            @Param("excludeId") Long excludeId);
}
