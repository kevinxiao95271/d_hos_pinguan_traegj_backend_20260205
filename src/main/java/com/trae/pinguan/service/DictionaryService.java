package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.DictionaryItem;
import com.trae.pinguan.repository.DictionaryItemRepository;
import com.trae.pinguan.web.dto.DictionaryItemRequest;
import com.trae.pinguan.web.dto.DictionaryItemUpdateRequest;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class DictionaryService {
    private final DictionaryItemRepository dictionaryItemRepository;

    public List<DictionaryItem> listByType(String type) {
        return dictionaryItemRepository.findByTypeAndActiveOrderByIdAsc(type, true);
    }

    public List<DictionaryItem> listAll() {
        return dictionaryItemRepository.findAll();
    }

    @Transactional
    public DictionaryItem create(DictionaryItemRequest request) {
        DictionaryItem item = DictionaryItem.builder()
                .type(request.getType())
                .code(request.getCode())
                .label(request.getLabel())
                .active(request.getActive())
                .createdAt(LocalDateTime.now())
                .build();
        return dictionaryItemRepository.save(item);
    }

    @Transactional
    public DictionaryItem update(Long id, DictionaryItemUpdateRequest request) {
        DictionaryItem item = dictionaryItemRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("字典不存在"));
        if (request.getType() != null) {
            item.setType(request.getType());
        }
        if (request.getCode() != null) {
            item.setCode(request.getCode());
        }
        if (request.getLabel() != null) {
            item.setLabel(request.getLabel());
        }
        if (request.getActive() != null) {
            item.setActive(request.getActive());
        }
        return dictionaryItemRepository.save(item);
    }

    @Transactional
    public void delete(Long id) {
        if (!dictionaryItemRepository.existsById(id)) {
            throw new IllegalArgumentException("字典不存在");
        }
        dictionaryItemRepository.deleteById(id);
    }
}
