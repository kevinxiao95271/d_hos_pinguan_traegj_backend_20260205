package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.RegistrationDraftProjectSummary;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RegistrationDraftProjectSummaryRepository extends JpaRepository<RegistrationDraftProjectSummary, Long> {
    Optional<RegistrationDraftProjectSummary> findByDraftId(Long draftId);
    void deleteByDraftId(Long draftId);
}
