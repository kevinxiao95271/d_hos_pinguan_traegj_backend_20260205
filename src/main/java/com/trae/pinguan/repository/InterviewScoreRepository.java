package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.InterviewScore;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import org.springframework.data.jpa.repository.JpaRepository;

public interface InterviewScoreRepository extends JpaRepository<InterviewScore, Long> {

    Optional<InterviewScore> findByReviewTaskId(Long reviewTaskId);

    List<InterviewScore> findByReviewTaskIdIn(Set<Long> reviewTaskIds);
}
