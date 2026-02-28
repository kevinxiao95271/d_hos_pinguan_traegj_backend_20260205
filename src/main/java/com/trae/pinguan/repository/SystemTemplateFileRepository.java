package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.SystemTemplateFile;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface SystemTemplateFileRepository extends JpaRepository<SystemTemplateFile, Long> {
    
    /**
     * 查询指定类型的激活模版
     */
    Optional<SystemTemplateFile> findByTemplateTypeAndIsActiveTrue(String templateType);
    
    /**
     * 查询所有激活模版
     */
    List<SystemTemplateFile> findByIsActiveTrue();
    
    /**
     * 查询指定类型的所有模版（含历史）
     */
    List<SystemTemplateFile> findByTemplateTypeOrderByVersionDesc(String templateType);
    
    /**
     * 获取指定类型的最大版本号
     */
    @Query("SELECT MAX(t.version) FROM SystemTemplateFile t WHERE t.templateType = :templateType")
    Integer findMaxVersionByType(@Param("templateType") String templateType);
    
    /**
     * 停用指定类型的所有模版
     */
    @Modifying
    @Query("UPDATE SystemTemplateFile t SET t.isActive = false WHERE t.templateType = :templateType")
    void deactivateByType(@Param("templateType") String templateType);
}
