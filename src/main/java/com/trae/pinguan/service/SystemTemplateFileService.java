package com.trae.pinguan.service;

import com.trae.pinguan.config.MinioProperties;
import com.trae.pinguan.domain.entity.SystemTemplateFile;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.SystemTemplateType;
import com.trae.pinguan.repository.SystemTemplateFileRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.SystemTemplateDTO;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class SystemTemplateFileService {
    private final SystemTemplateFileRepository repository;
    private final UserAccountRepository userAccountRepository;
    private final FileStorageService fileStorageService;
    private final MinioProperties minioProperties;
    
    /**
     * 上传新模版（自动版本递增，停用旧版本）
     */
    @Transactional
    public SystemTemplateDTO uploadTemplate(SystemTemplateType type, MultipartFile file, 
                                           Long uploaderId, String description) {
        // 1. 获取当前最大版本号
        Integer maxVersion = repository.findMaxVersionByType(type.getCode());
        int newVersion = (maxVersion == null) ? 1 : maxVersion + 1;
        
        // 2. 停用该类型的旧版本
        repository.deactivateByType(type.getCode());
        
        // 3. 存储文件到 MinIO
        String objectName = fileStorageService.storeSystemTemplate(type.getCode(), file);
        
        // 4. 获取上传人信息
        UserAccount uploader = null;
        if (uploaderId != null) {
            uploader = userAccountRepository.findById(uploaderId).orElse(null);
        }
        
        // 5. 创建新记录
        SystemTemplateFile template = SystemTemplateFile.builder()
            .templateType(type.getCode())
            .fileName(file.getOriginalFilename())
            .minioObjectName(objectName)
            .fileSize(file.getSize())
            .version(newVersion)
            .isActive(true)
            .uploadedBy(uploader)
            .uploadedAt(LocalDateTime.now())
            .description(description)
            .build();
        
        SystemTemplateFile saved = repository.save(template);
        return toDTO(saved);
    }
    
    /**
     * 获取指定类型的激活模版
     */
    public SystemTemplateDTO getActiveTemplate(SystemTemplateType type) {
        return repository.findByTemplateTypeAndIsActiveTrue(type.getCode())
            .map(this::toDTO)
            .orElse(null);
    }
    
    /**
     * 获取所有激活模版列表
     */
    public List<SystemTemplateDTO> getAllActiveTemplates() {
        return repository.findByIsActiveTrue().stream()
            .map(this::toDTO)
            .collect(Collectors.toList());
    }
    
    /**
     * 查看历史版本
     */
    public List<SystemTemplateDTO> listTemplateHistory(SystemTemplateType type) {
        return repository.findByTemplateTypeOrderByVersionDesc(type.getCode()).stream()
            .map(this::toDTO)
            .collect(Collectors.toList());
    }
    
    /**
     * 根据 ID 获取模版
     */
    public SystemTemplateFile getById(Long id) {
        return repository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("模版不存在"));
    }
    
    /**
     * 删除模版
     */
    @Transactional
    public void deleteTemplate(Long templateId) {
        SystemTemplateFile template = getById(templateId);
        
        // 删除 MinIO 文件
        fileStorageService.deleteSystemTemplate(template.getMinioObjectName());
        
        // 删除数据库记录
        repository.deleteById(templateId);
    }
    
    /**
     * 转换为 DTO
     */
    private SystemTemplateDTO toDTO(SystemTemplateFile entity) {
        return SystemTemplateDTO.builder()
            .id(entity.getId())
            .templateType(entity.getTemplateType())
            .fileName(entity.getFileName())
            .fileSize(entity.getFileSize())
            .version(entity.getVersion())
            .isActive(entity.getIsActive())
            .uploadedBy(entity.getUploadedBy() != null ? entity.getUploadedBy().getName() : null)
            .uploadedAt(entity.getUploadedAt())
            .description(entity.getDescription())
            .build();
    }
}
