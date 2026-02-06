package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.ActivityTemplate;
import com.trae.pinguan.repository.ActivityTemplateRepository;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class ActivityTemplateService {
    private final ActivityTemplateRepository activityTemplateRepository;
    private final FileStorageService fileStorageService;

    public List<ActivityTemplate> list(String type) {
        if (type == null || type.trim().isEmpty()) {
            return activityTemplateRepository.findAll();
        }
        return activityTemplateRepository.findByTypeOrderByIdAsc(type);
    }

    @Transactional
    public ActivityTemplate upload(String type, MultipartFile file) {
        String path = fileStorageService.store("activity-templates", file);
        ActivityTemplate template = ActivityTemplate.builder()
                .type(type)
                .fileName(file.getOriginalFilename())
                .fileUrl(path)
                .uploadedAt(LocalDateTime.now())
                .build();
        return activityTemplateRepository.save(template);
    }

    public ActivityTemplate get(Long id) {
        return activityTemplateRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("模板不存在"));
    }

    @Transactional
    public void delete(Long id) {
        ActivityTemplate template = get(id);
        activityTemplateRepository.deleteById(id);
        fileStorageService.delete(template.getFileUrl());
    }
}
