package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.web.dto.InstitutionCreateRequest;
import com.trae.pinguan.web.dto.InstitutionImportRequest;
import com.trae.pinguan.web.dto.InstitutionUpdateRequest;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class InstitutionService {
    private final InstitutionRepository institutionRepository;

    public List<Institution> listAll() {
        return institutionRepository.findAll();
    }

    public Institution get(Long id) {
        return institutionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
    }

    @Transactional
    public Institution create(InstitutionCreateRequest request) {
        institutionRepository.findByUscc(request.getUscc()).ifPresent(item -> {
            throw new IllegalArgumentException("统一社会信用代码已存在");
        });
        Institution institution = Institution.builder()
                .name(request.getName())
                .code(request.getCode())
                .uscc(request.getUscc())
                .region(request.getRegion())
                .createdAt(LocalDateTime.now())
                .build();
        return institutionRepository.save(institution);
    }

    @Transactional
    public Institution update(Long id, InstitutionUpdateRequest request) {
        Institution institution = get(id);
        if (request.getName() != null) {
            institution.setName(request.getName());
        }
        if (request.getCode() != null) {
            institution.setCode(request.getCode());
        }
        if (request.getUscc() != null && !request.getUscc().equals(institution.getUscc())) {
            institutionRepository.findByUscc(request.getUscc()).ifPresent(item -> {
                throw new IllegalArgumentException("统一社会信用代码已存在");
            });
            institution.setUscc(request.getUscc());
        }
        if (request.getRegion() != null) {
            institution.setRegion(request.getRegion());
        }
        return institutionRepository.save(institution);
    }

    @Transactional
    public void delete(Long id) {
        if (!institutionRepository.existsById(id)) {
            throw new IllegalArgumentException("机构不存在");
        }
        institutionRepository.deleteById(id);
    }

    @Transactional
    public List<Institution> importInstitutions(InstitutionImportRequest request) {
        List<Institution> items = request.getItems().stream()
                .map(item -> Institution.builder()
                        .name(item.getName())
                        .code(item.getCode())
                        .uscc(item.getUscc())
                        .region(item.getRegion())
                        .createdAt(LocalDateTime.now())
                        .build())
                .collect(Collectors.toList());
        return institutionRepository.saveAll(items);
    }
}
