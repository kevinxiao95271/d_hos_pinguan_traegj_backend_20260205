package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.DictionaryItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DictionaryItemRepository extends JpaRepository<DictionaryItem, Long> {
    
    /**
     * 根据类型查询字典项
     */
    List<DictionaryItem> findByTypeAndActiveTrue(String type);
    
    /**
     * 根据类型和代码查询
     */
    DictionaryItem findByTypeAndCode(String type, String code);
    
    /**
     * 查询所有启用的字典项
     */
    List<DictionaryItem> findByActiveTrue();
    
    /**
     * 根据代码查询字典项
     */
    java.util.Optional<DictionaryItem> findByCode(String code);
}
