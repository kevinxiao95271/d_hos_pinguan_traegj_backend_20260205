package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.RegistrationDraft;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RegistrationDraftRepository extends JpaRepository<RegistrationDraft, Long> {
    List<RegistrationDraft> findByApplicantIdOrderByUpdatedAtDesc(Long applicantId);

    List<RegistrationDraft> findByCompetition_IdAndInstitution_Id(Long competitionId, Long institutionId);
}
