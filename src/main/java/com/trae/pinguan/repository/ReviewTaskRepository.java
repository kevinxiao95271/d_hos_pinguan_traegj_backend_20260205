package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
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
    
    // 新增：支持多条件筛选的复杂查询（包含评委、分组、品管工具等信息）
    @Query("SELECT rt FROM ReviewTask rt " +
           "LEFT JOIN FETCH rt.registration r " +
           "LEFT JOIN FETCH r.institution i " +
           "LEFT JOIN FETCH rt.reviewer rev " +
           "LEFT JOIN FETCH rev.institution revInst " +
           "WHERE r.competition.id = :competitionId " +
           "AND rt.stage = :stage " +
           "AND (:status IS NULL OR rt.status = :status) " +
           "AND (:groupType IS NULL OR r.groupType = :groupType) " +
           "AND (:groupCode IS NULL OR r.groupCode = :groupCode) " +
           "AND (:reviewerId IS NULL OR rev.id = :reviewerId)")
    List<ReviewTask> findTasksWithFilters(
        @Param("competitionId") Long competitionId,
        @Param("stage") ReviewStage stage,
        @Param("status") ReviewStatus status,
        @Param("groupType") GroupType groupType,
        @Param("groupCode") String groupCode,
        @Param("reviewerId") Long reviewerId
    );
    
    // 分页查询：先查询ID列表（不带JOIN FETCH，避免分页问题）
    @Query("SELECT rt.id FROM ReviewTask rt " +
           "JOIN rt.registration r " +
           "LEFT JOIN rt.reviewer rev " +
           "WHERE r.competition.id = :competitionId " +
           "AND rt.stage = :stage " +
           "AND (:status IS NULL OR rt.status = :status) " +
           "AND (:groupType IS NULL OR r.groupType = :groupType) " +
           "AND (:groupCode IS NULL OR r.groupCode = :groupCode) " +
           "AND (:reviewerId IS NULL OR rev.id = :reviewerId)")
    Page<Long> findTaskIdsWithFilters(
        @Param("competitionId") Long competitionId,
        @Param("stage") ReviewStage stage,
        @Param("status") ReviewStatus status,
        @Param("groupType") GroupType groupType,
        @Param("groupCode") String groupCode,
        @Param("reviewerId") Long reviewerId,
        Pageable pageable
    );
    
    // 根据ID列表获取完整数据（带JOIN FETCH）
    @Query("SELECT rt FROM ReviewTask rt " +
           "LEFT JOIN FETCH rt.registration r " +
           "LEFT JOIN FETCH r.institution i " +
           "LEFT JOIN FETCH rt.reviewer rev " +
           "LEFT JOIN FETCH rev.institution revInst " +
           "WHERE rt.id IN :ids " +
           "ORDER BY rt.id")
    List<ReviewTask> findByIdsWithFetch(@Param("ids") List<Long> ids);
}
