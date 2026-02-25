package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.Institution;
import java.util.List;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface InstitutionRepository extends JpaRepository<Institution, Long>, JpaSpecificationExecutor<Institution> {
    Optional<Institution> findByUscc(String uscc);
    
    /**
     * 高性能搜索：支持多条件组合查询
     */
    @Query("SELECT i FROM Institution i WHERE " +
           "(:keyword IS NULL OR i.name LIKE %:keyword% OR i.region LIKE %:keyword%) AND " +
           "(:region IS NULL OR i.region = :region) AND " +
           "(:level IS NULL OR i.level = :level)")
    Page<Institution> searchInstitutions(
        @Param("keyword") String keyword,
        @Param("region") String region,
        @Param("level") String level,
        Pageable pageable
    );
    
    /**
     * 按名称前缀快速查找（用于自动完成）
     */
    @Query("SELECT i FROM Institution i WHERE i.name LIKE :prefix% ORDER BY i.name ASC")
    Page<Institution> findByNameStartsWith(@Param("prefix") String prefix, Pageable pageable);
    
    /**
     * 获取热门地区（有机构数量最多的地区）
     */
    @Query("SELECT i.region, COUNT(i) as cnt FROM Institution i " +
           "WHERE i.region IS NOT NULL " +
           "GROUP BY i.region " +
           "ORDER BY cnt DESC")
    List<Object[]> getHotRegions(Pageable pageable);
    
    List<Institution> findByRegion(String region);
    
    @Query("SELECT DISTINCT i.region FROM Institution i WHERE i.region IS NOT NULL ORDER BY i.region")
    List<String> findAllRegions();
    
    @Query("SELECT DISTINCT i.level FROM Institution i WHERE i.level IS NOT NULL ORDER BY i.level")
    List<String> findAllLevels();
    
    /**
     * 统计各地区机构数量
     */
    @Query("SELECT i.region, COUNT(i) FROM Institution i WHERE i.region IS NOT NULL GROUP BY i.region")
    List<Object[]> countByRegion();
}
