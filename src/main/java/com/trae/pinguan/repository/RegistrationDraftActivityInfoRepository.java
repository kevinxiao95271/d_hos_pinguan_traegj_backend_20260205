package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.RegistrationDraftActivityInfo;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RegistrationDraftActivityInfoRepository extends JpaRepository<RegistrationDraftActivityInfo, Long> {
    Optional<RegistrationDraftActivityInfo> findByDraftId(Long draftId);
    void deleteByDraftId(Long draftId);
}
