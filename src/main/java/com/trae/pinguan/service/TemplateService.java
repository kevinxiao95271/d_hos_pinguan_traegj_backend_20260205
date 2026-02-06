package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.entity.CompetitionTemplate;
import com.trae.pinguan.repository.CompetitionRepository;
import com.trae.pinguan.repository.CompetitionTemplateRepository;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class TemplateService {
    private final CompetitionRepository competitionRepository;
    private final CompetitionTemplateRepository templateRepository;
    private final FileStorageService fileStorageService;

    public List<CompetitionTemplate> list(Long competitionId) {
        return templateRepository.findByCompetitionId(competitionId);
    }

    public CompetitionTemplate get(Long competitionId, Long templateId) {
        CompetitionTemplate template = templateRepository.findById(templateId)
                .orElseThrow(() -> new IllegalArgumentException("模板不存在"));
        if (template.getCompetition() == null || !template.getCompetition().getId().equals(competitionId)) {
            throw new IllegalArgumentException("模板不属于赛事");
        }
        return template;
    }

    @Transactional
    public CompetitionTemplate upload(Long competitionId, String type, MultipartFile file) {
        Competition competition = competitionRepository.findById(competitionId)
                .orElseThrow(() -> new IllegalArgumentException("赛事不存在"));
        String path = fileStorageService.store(competitionId, file);
        CompetitionTemplate template = CompetitionTemplate.builder()
                .competition(competition)
                .type(type)
                .fileName(file.getOriginalFilename())
                .fileUrl(path)
                .uploadedAt(LocalDateTime.now())
                .build();
        return templateRepository.save(template);
    }

    @Transactional
    public void delete(Long competitionId, Long templateId) {
        CompetitionTemplate template = get(competitionId, templateId);
        templateRepository.deleteById(templateId);
        fileStorageService.delete(template.getFileUrl());
    }
}
