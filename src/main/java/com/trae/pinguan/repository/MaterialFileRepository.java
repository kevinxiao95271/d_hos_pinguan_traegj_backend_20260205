package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.MaterialFile;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface MaterialFileRepository extends JpaRepository<MaterialFile, Long> {
    List<MaterialFile> findByRegistrationId(Long registrationId);
    
    /**
     * 批量查询多个报名的材料文件
     */
    @Query("SELECT m FROM MaterialFile m WHERE m.registration.id IN :registrationIds")
    List<MaterialFile> findByRegistrationIdIn(@Param("registrationIds") List<Long> registrationIds);
}
