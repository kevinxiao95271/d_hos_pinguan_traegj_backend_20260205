package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ReviewerInstitutionChange;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReviewerInstitutionChangeRepository extends JpaRepository<ReviewerInstitutionChange, Long> {
    List<ReviewerInstitutionChange> findByReviewerIdOrderByChangedAtDesc(Long reviewerId);
}
