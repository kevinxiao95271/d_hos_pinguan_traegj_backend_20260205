package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.MaterialFile;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.repository.MaterialFileRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import java.security.MessageDigest;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
@RequiredArgsConstructor
public class MaterialService {
    private final RegistrationRepository registrationRepository;
    private final MaterialFileRepository materialFileRepository;
    private final FileStorageService fileStorageService;
    
    private static final long MAX_FILE_SIZE = 200 * 1024 * 1024; // 200MB
    private static final String PAYMENT_PROOF_TYPE = "payment_proof";
    private static final String EVIDENCE_TYPE = "EVIDENCE";
    private static final int EVIDENCE_MAX_COUNT = 5;
    private static final String REGISTRATION_FORM_DOC_TYPE = "REGISTRATION_FORM_DOC";
    private static final String REGISTRATION_FORM_PDF_TYPE = "REGISTRATION_FORM_PDF";
    private static final String[] ALLOWED_EXTENSIONS = {
        "pdf", "doc", "docx", "xls", "xlsx", 
        "ppt", "pptx", "zip", "rar", 
        "jpg", "jpeg", "png", "gif"
    };
    private static final Set<String> PAYMENT_PROOF_ALLOWED_EXTENSIONS = new HashSet<>(
            Arrays.asList("jpg", "jpeg", "png", "gif", "webp")
    );
    private static final Set<String> REG_FORM_DOC_ALLOWED_EXTENSIONS = new HashSet<>(
            Arrays.asList("doc", "docx")
    );
    private static final Set<String> REG_FORM_PDF_ALLOWED_EXTENSIONS = new HashSet<>(
            Arrays.asList("pdf")
    );

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
        String normalizedType = normalizeType(type);
        boolean isPaymentProof = isPaymentProofType(normalizedType);
        
        // 验证文件大小
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new IllegalArgumentException("文件大小不能超过200MB");
        }
        
        // 验证文件类型
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || originalFilename.isEmpty()) {
            throw new IllegalArgumentException("文件名不能为空");
        }
        
        String extension = getFileExtension(originalFilename);
        if (isPaymentProof && !isPaymentProofExtension(extension)) {
            throw new IllegalArgumentException("支付凭证仅支持图片格式: jpg, jpeg, png, gif, webp");
        }
        validateTypeSpecificExtension(normalizedType, extension);
        if (!isAllowedExtension(extension)) {
            throw new IllegalArgumentException("不支持的文件类型，仅支持: pdf, doc, docx, xls, xlsx, ppt, pptx, zip, rar, jpg, jpeg, png, gif");
        }

        String fileHash = isPaymentProof ? computeSha256(file) : null;
        validateTypeAndHashRule(normalizedType, fileHash);

        // payment_proof: append, ignore duplicates
        // EVIDENCE: append, max 5 files
        // other types: keep only latest
        if (isPaymentProof) {
            MaterialFile existing = materialFileRepository
                    .findFirstByRegistrationIdAndTypeAndFileHash(registrationId, normalizedType, fileHash)
                    .orElse(null);
            if (existing != null) {
                return existing;
            }
        } else if (EVIDENCE_TYPE.equalsIgnoreCase(normalizedType)) {
            List<MaterialFile> existing = materialFileRepository.findByRegistrationIdAndType(registrationId, normalizedType);
            if (existing.size() >= EVIDENCE_MAX_COUNT) {
                throw new IllegalArgumentException("佐证材料最多上传 " + EVIDENCE_MAX_COUNT + " 个文件");
            }
        } else {
            List<MaterialFile> oldFiles = materialFileRepository.findByRegistrationIdAndType(registrationId, normalizedType);
            for (MaterialFile oldFile : oldFiles) {
                try {
                    fileStorageService.delete(oldFile.getFileUrl());
                } catch (Exception ex) {
                    // ignore MinIO delete failure
                }
                materialFileRepository.delete(oldFile);
            }
        }
        
        String path = fileStorageService.store(registrationId, file);
        MaterialFile materialFile = MaterialFile.builder()
                .registration(registration)
                .type(normalizedType)
                .fileName(file.getOriginalFilename())
                .fileUrl(path)
                .fileHash(fileHash)
                .uploadedAt(LocalDateTime.now())
                .build();
        try {
            return materialFileRepository.save(materialFile);
        } catch (DataIntegrityViolationException e) {
            // 并发下可能触发唯一索引冲突，回退为查询已有记录
            if (isPaymentProof && fileHash != null) {
                return materialFileRepository
                        .findFirstByRegistrationIdAndTypeAndFileHash(registrationId, normalizedType, fileHash)
                        .orElseThrow(() -> e);
            }
            throw e;
        }
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

    private boolean isPaymentProofExtension(String extension) {
        return PAYMENT_PROOF_ALLOWED_EXTENSIONS.contains(extension.toLowerCase(Locale.ROOT));
    }

    private void validateTypeSpecificExtension(String type, String extension) {
        String ext = extension.toLowerCase(Locale.ROOT);
        if (REGISTRATION_FORM_DOC_TYPE.equalsIgnoreCase(type)
                && !REG_FORM_DOC_ALLOWED_EXTENSIONS.contains(ext)) {
            throw new IllegalArgumentException("REGISTRATION_FORM_DOC 仅支持 Word: doc, docx");
        }
        if (REGISTRATION_FORM_PDF_TYPE.equalsIgnoreCase(type)
                && !REG_FORM_PDF_ALLOWED_EXTENSIONS.contains(ext)) {
            throw new IllegalArgumentException("REGISTRATION_FORM_PDF 仅支持 PDF");
        }
    }

    private String normalizeType(String type) {
        if (type == null || type.trim().isEmpty()) {
            throw new IllegalArgumentException("材料类型不能为空");
        }
        return type.trim();
    }

    private boolean isPaymentProofType(String type) {
        return PAYMENT_PROOF_TYPE.equalsIgnoreCase(type);
    }

    private void validateTypeAndHashRule(String type, String fileHash) {
        if (isPaymentProofType(type)) {
            if (fileHash == null || fileHash.trim().isEmpty()) {
                throw new IllegalArgumentException("payment_proof 类型要求 file_hash 必填");
            }
        } else if (fileHash != null) {
            throw new IllegalArgumentException("非 payment_proof 类型要求 file_hash 为 NULL");
        }
    }

    private String computeSha256(MultipartFile file) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(file.getBytes());
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new IllegalArgumentException("计算文件哈希失败");
        }
    }

    @Transactional
    public void delete(Long materialId) {
        materialFileRepository.findById(materialId).ifPresent(material -> {
            try {
                fileStorageService.delete(material.getFileUrl());
            } catch (Exception ex) {
                // MinIO 删除失败不阻塞业务
            }
            materialFileRepository.delete(material);
        });
    }
}
