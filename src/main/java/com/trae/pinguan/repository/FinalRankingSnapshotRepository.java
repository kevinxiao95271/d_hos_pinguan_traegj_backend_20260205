package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.FinalRankingSnapshot;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface FinalRankingSnapshotRepository extends JpaRepository<FinalRankingSnapshot, Long> {

    List<FinalRankingSnapshot> findByCompetitionIdOrderBySessionCodeAscSessionRankAsc(Long competitionId);

    List<FinalRankingSnapshot> findByCompetitionIdAndSessionCodeOrderBySessionRankAsc(
            Long competitionId, String sessionCode);

    @Modifying
    @Query("DELETE FROM FinalRankingSnapshot f WHERE f.competitionId = :competitionId")
    void deleteByCompetitionId(@Param("competitionId") Long competitionId);

    @Modifying
    @Query("DELETE FROM FinalRankingSnapshot f WHERE f.competitionId = :competitionId AND f.sessionCode = :sessionCode")
    void deleteByCompetitionIdAndSessionCode(@Param("competitionId") Long competitionId,
                                             @Param("sessionCode") String sessionCode);
}
