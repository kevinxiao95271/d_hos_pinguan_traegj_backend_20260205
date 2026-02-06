package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.InstitutionUpdateRequest;
import com.trae.pinguan.domain.enums.ApprovalStatus;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface InstitutionUpdateRequestRepository extends JpaRepository<InstitutionUpdateRequest, Long> {
    List<InstitutionUpdateRequest> findByStatus(ApprovalStatus status);
}
