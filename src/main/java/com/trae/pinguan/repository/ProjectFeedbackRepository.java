package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ProjectFeedback;
import com.trae.pinguan.domain.enums.ReviewStage;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ProjectFeedbackRepository extends JpaRepository<ProjectFeedback, Long> {
    Optional<ProjectFeedback> findByRegistrationIdAndStage(Long registrationId, ReviewStage stage);

    List<ProjectFeedback> findByRegistrationIdAndPublishedTrueOrderByUpdatedAtDesc(Long registrationId);

    List<ProjectFeedback> findByRegistrationIdInAndStage(Collection<Long> registrationIds, ReviewStage stage);

    @Query("select pf from ProjectFeedback pf " +
            "join fetch pf.registration r " +
            "left join fetch r.institution " +
            "where r.competition.id = :competitionId and pf.stage = :stage")
    List<ProjectFeedback> findByCompetitionIdAndStageWithRegistration(
            @Param("competitionId") Long competitionId,
            @Param("stage") ReviewStage stage);

    @Query("select pf from ProjectFeedback pf " +
            "join fetch pf.registration r " +
            "left join fetch r.institution i " +
            "where r.competition.id = :competitionId " +
            "and pf.stage = :stage " +
            "and (:groupType is null or r.groupType = :groupType) " +
            "and (:groupCode is null or lower(r.groupCode) = lower(:groupCode)) " +
            "and (:projectName is null or lower(r.projectName) like lower(concat('%', :projectName, '%'))) " +
            "and (:institutionName is null or lower(i.name) like lower(concat('%', :institutionName, '%'))) " +
            "and (:published is null or pf.published = :published) " +
            "order by r.id asc")
    List<ProjectFeedback> findFilteredByCompetitionAndStageWithRegistration(
            @Param("competitionId") Long competitionId,
            @Param("stage") ReviewStage stage,
            @Param("groupType") com.trae.pinguan.domain.enums.GroupType groupType,
            @Param("groupCode") String groupCode,
            @Param("projectName") String projectName,
            @Param("institutionName") String institutionName,
            @Param("published") Boolean published);

    @Query("select count(pf) from ProjectFeedback pf join pf.registration r " +
            "where r.competition.id = :competitionId and pf.stage = :stage")
    long countByCompetitionIdAndStage(@Param("competitionId") Long competitionId,
                                      @Param("stage") ReviewStage stage);
}
