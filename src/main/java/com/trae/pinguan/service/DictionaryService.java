package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.DictionaryItem;
import com.trae.pinguan.repository.DictionaryItemRepository;
import com.trae.pinguan.web.dto.DictionaryItemRequest;
import com.trae.pinguan.web.dto.DictionaryItemUpdateRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Slf4j
@RequiredArgsConstructor
public class DictionaryService {
    
    private final DictionaryItemRepository repository;
    
    /**
     * 根据类型获取字典项列表
     */
    public List<DictionaryItem> getByType(String type) {
        log.info("获取字典项，类型: {}", type);
        return repository.findByTypeAndActiveTrue(type);
    }
    
    /**
     * 获取所有启用的字典项
     */
    public List<DictionaryItem> getAllActive() {
        log.info("获取所有启用的字典项");
        return repository.findByActiveTrue();
    }
    
    /**
     * 创建字典项
     */
    @Transactional
    public DictionaryItem create(DictionaryItemRequest request) {
        log.info("创建字典项: type={}, code={}", request.getType(), request.getCode());
        
        // 检查是否已存在
        DictionaryItem existing = repository.findByTypeAndCode(request.getType(), request.getCode());
        if (existing != null) {
            throw new IllegalArgumentException("字典项已存在: " + request.getType() + "." + request.getCode());
        }
        
        DictionaryItem item = DictionaryItem.builder()
                .type(request.getType())
                .code(request.getCode())
                .label(request.getLabel())
                .active(request.getActive() != null ? request.getActive() : true)
                .build();
        
        return repository.save(item);
    }
    
    /**
     * 更新字典项
     */
    @Transactional
    public DictionaryItem update(Long id, DictionaryItemUpdateRequest request) {
        log.info("更新字典项: id={}", id);
        
        DictionaryItem item = repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("字典项不存在: " + id));
        
        if (request.getLabel() != null) {
            item.setLabel(request.getLabel());
        }
        if (request.getActive() != null) {
            item.setActive(request.getActive());
        }
        
        return repository.save(item);
    }
    
    /**
     * 删除字典项（逻辑删除）
     */
    @Transactional
    public void delete(Long id) {
        log.info("删除字典项: id={}", id);
        
        DictionaryItem item = repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("字典项不存在: " + id));
        
        item.setActive(false);
        repository.save(item);
    }
}
