package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ReviewScore;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReviewScoreRepository extends JpaRepository<ReviewScore, Long> {
    Optional<ReviewScore> findByReviewTaskId(Long reviewTaskId);
    List<ReviewScore> findByReviewTaskIdIn(Collection<Long> taskIds);
}
