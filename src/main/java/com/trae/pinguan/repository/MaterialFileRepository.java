package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.MaterialFile;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface MaterialFileRepository extends JpaRepository<MaterialFile, Long> {
    List<MaterialFile> findByRegistrationId(Long registrationId);
    
    /**
     * 根据报名ID和文件类型查询（用于删除旧文件）
     */
    List<MaterialFile> findByRegistrationIdAndType(Long registrationId, String type);

    Optional<MaterialFile> findFirstByRegistrationIdAndTypeAndFileHash(Long registrationId, String type, String fileHash);
    
    /**
     * 批量查询多个报名的材料文件
     */
    @Query("SELECT m FROM MaterialFile m WHERE m.registration.id IN :registrationIds")
    List<MaterialFile> findByRegistrationIdIn(@Param("registrationIds") List<Long> registrationIds);
}
