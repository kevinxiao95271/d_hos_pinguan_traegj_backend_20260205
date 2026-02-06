package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ActivityTemplate;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ActivityTemplateRepository extends JpaRepository<ActivityTemplate, Long> {
    List<ActivityTemplate> findByTypeOrderByIdAsc(String type);
}
