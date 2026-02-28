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
    
    private static final long MAX_FILE_SIZE = 30 * 1024 * 1024; // 30MB
    private static final String[] ALLOWED_EXTENSIONS = {
        "pdf", "doc", "docx", "xls", "xlsx", 
        "ppt", "pptx", "zip", "rar", 
        "jpg", "jpeg", "png", "gif"
    };

    public List<MaterialFile> list(Long registrationId) {
        return materialFileRepository.findByRegistrationId(registrationId);
    }
    
    public MaterialFile getById(Long materialId) {
        return materialFileRepository.findById(materialId)
                .orElseThrow(() -> new IllegalArgumentException("材料文件不存在"));
    }

    @Transactional
    public MaterialFile upload(Long registrationId, String type, MultipartFile file) {
        Registration registration = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        
        // 验证文件大小
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new IllegalArgumentException("文件大小不能超过30MB");
        }
        
        // 验证文件类型
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || originalFilename.isEmpty()) {
            throw new IllegalArgumentException("文件名不能为空");
        }
        
        String extension = getFileExtension(originalFilename);
        if (!isAllowedExtension(extension)) {
            throw new IllegalArgumentException("不支持的文件类型，仅支持: pdf, doc, docx, xls, xlsx, ppt, pptx, zip, rar, jpg, jpeg, png, gif");
        }
        
        // 删除该报名下相同type的旧文件（只保留最新的一个）
        List<MaterialFile> oldFiles = materialFileRepository.findByRegistrationIdAndType(registrationId, type);
        for (MaterialFile oldFile : oldFiles) {
            try {
                // 删除MinIO中的文件
                fileStorageService.delete(oldFile.getFileUrl());
            } catch (Exception ex) {
                // 如果删除MinIO文件失败，记录但继续（避免阻塞上传）
                // 实际生产环境建议记录日志
            }
            // 删除数据库记录
            materialFileRepository.delete(oldFile);
        }
        
        // 保存新文件
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
    
    private String getFileExtension(String filename) {
        int lastDotIndex = filename.lastIndexOf('.');
        if (lastDotIndex == -1 || lastDotIndex == filename.length() - 1) {
            return "";
        }
        return filename.substring(lastDotIndex + 1).toLowerCase();
    }
    
    private boolean isAllowedExtension(String extension) {
        for (String allowed : ALLOWED_EXTENSIONS) {
            if (allowed.equalsIgnoreCase(extension)) {
                return true;
            }
        }
        return false;
    }

    @Transactional
    public void delete(Long materialId) {
        materialFileRepository.deleteById(materialId);
    }
}
