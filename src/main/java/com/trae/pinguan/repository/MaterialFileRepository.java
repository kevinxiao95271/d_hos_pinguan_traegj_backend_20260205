package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.MaterialFile;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MaterialFileRepository extends JpaRepository<MaterialFile, Long> {
    List<MaterialFile> findByRegistrationId(Long registrationId);
}
