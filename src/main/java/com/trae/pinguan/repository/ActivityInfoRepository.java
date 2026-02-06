package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ActivityInfo;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ActivityInfoRepository extends JpaRepository<ActivityInfo, Long> {
    Optional<ActivityInfo> findByRegistrationId(Long registrationId);
}
