package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ConstInitInstitution;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

/**
 * 常量机构库Repository（仅用于注册搜索）
 */
public interface ConstInitInstitutionRepository extends JpaRepository<ConstInitInstitution, Long>, JpaSpecificationExecutor<ConstInitInstitution> {
    
    Optional<ConstInitInstitution> findByUscc(String uscc);
    
    Optional<ConstInitInstitution> findByCode(String code);
    
    /**
     * 高性能搜索（注册时使用）
     * 排序规则：等级优先（三级>二级>一级>其他），然后按名称
     */
    @Query(value = "SELECT c FROM ConstInitInstitution c WHERE " +
           "(:keyword IS NULL OR :keyword = '' OR c.name LIKE CONCAT('%', :keyword, '%') OR c.region LIKE CONCAT('%', :keyword, '%')) AND " +
           "(:region IS NULL OR :region = '' OR c.region = :region) AND " +
           "(:level IS NULL OR :level = '' OR c.level = :level) " +
           "ORDER BY " +
           "CASE " +
           "  WHEN c.level = '三级' THEN 1 " +
           "  WHEN c.level = '二级' THEN 2 " +
           "  WHEN c.level = '一级' THEN 3 " +
           "  ELSE 4 " +
           "END, " +
           "c.name ASC",
           countQuery = "SELECT COUNT(c) FROM ConstInitInstitution c WHERE " +
           "(:keyword IS NULL OR :keyword = '' OR c.name LIKE CONCAT('%', :keyword, '%') OR c.region LIKE CONCAT('%', :keyword, '%')) AND " +
           "(:region IS NULL OR :region = '' OR c.region = :region) AND " +
           "(:level IS NULL OR :level = '' OR c.level = :level)")
    Page<ConstInitInstitution> searchInstitutions(
            @Param("keyword") String keyword,
            @Param("region") String region,
            @Param("level") String level,
            Pageable pageable
    );
    
    /**
     * 自动完成
     */
    Page<ConstInitInstitution> findByNameStartsWith(String prefix, Pageable pageable);
    
    /**
     * 获取所有地区
     */
    @Query("SELECT DISTINCT c.region FROM ConstInitInstitution c WHERE c.region IS NOT NULL ORDER BY c.region")
    List<String> findAllRegions();
    
    /**
     * 获取所有等级
     */
    @Query("SELECT DISTINCT c.level FROM ConstInitInstitution c WHERE c.level IS NOT NULL ORDER BY c.level")
    List<String> findAllLevels();
    
    /**
     * 热门地区统计
     */
    @Query("SELECT c.region, COUNT(c) FROM ConstInitInstitution c WHERE c.region IS NOT NULL GROUP BY c.region ORDER BY COUNT(c) DESC")
    List<Object[]> getHotRegions(Pageable pageable);
}
