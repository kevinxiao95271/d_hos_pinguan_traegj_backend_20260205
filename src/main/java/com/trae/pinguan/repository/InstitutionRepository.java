package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.Institution;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface InstitutionRepository extends JpaRepository<Institution, Long> {
    Optional<Institution> findByUscc(String uscc);
}
