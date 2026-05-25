package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ScoringSnapshot;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ScoringSnapshotRepository extends JpaRepository<ScoringSnapshot, Long> {

    List<ScoringSnapshot> findByCompetitionIdAndStageOrderByIrankAsc(Long competitionId, ReviewStage stage);

    List<ScoringSnapshot> findByCompetitionIdAndStageAndGroupTypeOrderByIrankAsc(
            Long competitionId, ReviewStage stage, GroupType groupType);

    Optional<ScoringSnapshot> findByRegistrationIdAndStage(Long registrationId, ReviewStage stage);

    @Modifying
    @Query("DELETE FROM ScoringSnapshot s WHERE s.competitionId = :competitionId AND s.stage = :stage")
    void deleteByCompetitionIdAndStage(@Param("competitionId") Long competitionId,
                                       @Param("stage") ReviewStage stage);

    @Modifying
    @Query("DELETE FROM ScoringSnapshot s WHERE s.competitionId = :competitionId AND s.stage = :stage AND s.groupType = :groupType")
    void deleteByCompetitionIdAndStageAndGroupType(@Param("competitionId") Long competitionId,
                                                   @Param("stage") ReviewStage stage,
                                                   @Param("groupType") GroupType groupType);

    // ── FINAL 阶段专用（groupCode 存 sessionCode）────────────────────────────

    List<ScoringSnapshot> findByCompetitionIdAndStageAndGroupCodeOrderByIrankAsc(
            Long competitionId, ReviewStage stage, String groupCode);
}
