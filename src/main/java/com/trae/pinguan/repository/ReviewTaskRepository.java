package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ReviewTaskRepository extends JpaRepository<ReviewTask, Long> {
    List<ReviewTask> findByRegistrationId(Long registrationId);
    List<ReviewTask> findByRegistrationIdAndStage(Long registrationId, ReviewStage stage);
    
    // 使用JOIN FETCH优化查询，避免N+1问题
    @Query("SELECT rt FROM ReviewTask rt LEFT JOIN FETCH rt.registration r LEFT JOIN FETCH r.institution WHERE rt.reviewer.id = :reviewerId")
    List<ReviewTask> findByReviewerId(@Param("reviewerId") Long reviewerId);
    
    List<ReviewTask> findByReviewerIdAndStage(Long reviewerId, ReviewStage stage);
    List<ReviewTask> findByStageAndStatus(ReviewStage stage, ReviewStatus status);
    List<ReviewTask> findByStageAndRegistrationCompetitionId(ReviewStage stage, Long competitionId);
    List<ReviewTask> findByStageAndStatusAndRegistrationCompetitionId(ReviewStage stage, ReviewStatus status, Long competitionId);

    // JOIN FETCH变体，避免listTasksForAdmin/summaryByStage/feedbackByStage的4N懒加载
    @Query("SELECT rt FROM ReviewTask rt " +
           "LEFT JOIN FETCH rt.registration r " +
           "LEFT JOIN FETCH r.institution " +
           "LEFT JOIN FETCH rt.reviewer rv " +
           "LEFT JOIN FETCH rv.institution " +
           "WHERE rt.stage = :stage AND r.competition.id = :competitionId " +
           "ORDER BY COALESCE(rt.updatedAt, rt.createdAt) DESC")
    List<ReviewTask> findWithDetailsByStageAndCompetitionId(
            @Param("stage") ReviewStage stage,
            @Param("competitionId") Long competitionId);

    @Query("SELECT rt FROM ReviewTask rt " +
           "LEFT JOIN FETCH rt.registration r " +
           "LEFT JOIN FETCH r.institution " +
           "LEFT JOIN FETCH rt.reviewer rv " +
           "LEFT JOIN FETCH rv.institution " +
           "WHERE rt.stage = :stage AND rt.status = :status AND r.competition.id = :competitionId " +
           "ORDER BY COALESCE(rt.updatedAt, rt.createdAt) DESC")
    List<ReviewTask> findWithDetailsByStageAndStatusAndCompetitionId(
            @Param("stage") ReviewStage stage,
            @Param("status") ReviewStatus status,
            @Param("competitionId") Long competitionId);
    
    /**
     * 检查评委是否有权限查看指定报名的材料（是否有评审任务）
     */
    @Query("SELECT COUNT(rt) > 0 FROM ReviewTask rt WHERE rt.reviewer.id = :reviewerId AND rt.registration.id = :registrationId")
    boolean existsByReviewerIdAndRegistrationId(@Param("reviewerId") Long reviewerId, @Param("registrationId") Long registrationId);
}
