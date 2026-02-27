package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.DictionaryItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DictionaryItemRepository extends JpaRepository<DictionaryItem, Long> {
    
    /**
     * 根据类型查询字典项（'other'选项在最后）
     */
    @Query("SELECT d FROM DictionaryItem d " +
           "WHERE d.type = :type AND d.active = true " +
           "ORDER BY CASE WHEN d.code = 'other' THEN 1 ELSE 0 END, d.id")
    List<DictionaryItem> findByTypeAndActiveTrue(@Param("type") String type);
    
    /**
     * 根据类型和代码查询
     */
    DictionaryItem findByTypeAndCode(String type, String code);
    
    /**
     * 查询所有启用的字典项（'other'选项在最后）
     */
    @Query("SELECT d FROM DictionaryItem d " +
           "WHERE d.active = true " +
           "ORDER BY d.type, CASE WHEN d.code = 'other' THEN 1 ELSE 0 END, d.id")
    List<DictionaryItem> findByActiveTrue();
    
    /**
     * 根据代码查询字典项
     */
    java.util.Optional<DictionaryItem> findByCode(String code);
}
