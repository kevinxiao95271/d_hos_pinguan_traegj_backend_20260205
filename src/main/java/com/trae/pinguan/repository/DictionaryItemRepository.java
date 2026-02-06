package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.DictionaryItem;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DictionaryItemRepository extends JpaRepository<DictionaryItem, Long> {
    List<DictionaryItem> findByTypeAndActiveOrderByIdAsc(String type, Boolean active);
    Optional<DictionaryItem> findFirstByTypeAndCodeAndActiveTrue(String type, String code);
}
