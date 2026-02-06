package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.MaterialFile;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.repository.MaterialFileRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class MaterialService {
    private final RegistrationRepository registrationRepository;
    private final MaterialFileRepository materialFileRepository;
    private final FileStorageService fileStorageService;

    public List<MaterialFile> list(Long registrationId) {
        return materialFileRepository.findByRegistrationId(registrationId);
    }

    @Transactional
    public MaterialFile upload(Long registrationId, String type, MultipartFile file) {
        Registration registration = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        String path = fileStorageService.store(registrationId, file);
        MaterialFile materialFile = MaterialFile.builder()
                .registration(registration)
                .type(type)
                .fileName(file.getOriginalFilename())
                .fileUrl(path)
                .uploadedAt(LocalDateTime.now())
                .build();
        return materialFileRepository.save(materialFile);
    }

    @Transactional
    public void delete(Long materialId) {
        materialFileRepository.deleteById(materialId);
    }
}
