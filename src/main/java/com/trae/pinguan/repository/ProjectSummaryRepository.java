package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ProjectSummary;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProjectSummaryRepository extends JpaRepository<ProjectSummary, Long> {
    Optional<ProjectSummary> findByRegistrationId(Long registrationId);
}
