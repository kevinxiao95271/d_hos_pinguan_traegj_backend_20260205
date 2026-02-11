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
    List<ReviewTask> findByRegistrationCompetitionId(Long competitionId);
    List<ReviewTask> findByStatusAndRegistrationCompetitionId(ReviewStatus status, Long competitionId);
}
