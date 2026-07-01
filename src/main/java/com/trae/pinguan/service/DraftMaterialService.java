package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.RegistrationDraft;
import com.trae.pinguan.domain.entity.RegistrationDraftMaterialFile;
import com.trae.pinguan.repository.RegistrationDraftMaterialFileRepository;
import com.trae.pinguan.repository.RegistrationDraftRepository;
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
public class DraftMaterialService {
    private final RegistrationDraftRepository draftRepository;
    private final RegistrationDraftMaterialFileRepository draftMaterialRepository;
    private final FileStorageService fileStorageService;

    private static final long MAX_FILE_SIZE = 200 * 1024 * 1024;
    private static final String PAYMENT_PROOF_TYPE = "payment_proof";
    private static final String EVIDENCE_TYPE = "EVIDENCE";
    private static final int EVIDENCE_MAX_COUNT = 5;
    private static final String REGISTRATION_FORM_DOC_TYPE = "REGISTRATION_FORM_DOC";
    private static final String REGISTRATION_FORM_PDF_TYPE = "REGISTRATION_FORM_PDF";
    private static final String REPORT_TYPE = "REPORT";
    private static final String[] ALLOWED_EXTENSIONS = {
            "pdf", "doc", "docx", "xls", "xlsx",
            "ppt", "pptx", "zip", "rar",
            "jpg", "jpeg", "png", "gif"
    };
    private static final Set<String> PAYMENT_PROOF_ALLOWED_EXTENSIONS = new HashSet<>(
            Arrays.asList("jpg", "jpeg", "png", "gif", "webp"));
    private static final Set<String> REG_FORM_DOC_ALLOWED_EXTENSIONS = new HashSet<>(
            Arrays.asList("doc", "docx"));
    private static final Set<String> REG_FORM_PDF_ALLOWED_EXTENSIONS = new HashSet<>(
            Arrays.asList("pdf"));

    public List<RegistrationDraftMaterialFile> list(Long draftId) {
        return draftMaterialRepository.findByDraftId(draftId);
    }

    public RegistrationDraftMaterialFile getById(Long materialId) {
        return draftMaterialRepository.findById(materialId)
                .orElseThrow(() -> new IllegalArgumentException("材料文件不存在"));
    }

    @Transactional
    public RegistrationDraftMaterialFile upload(Long draftId, String type, MultipartFile file) {
        RegistrationDraft draft = draftRepository.findById(draftId)
                .orElseThrow(() -> new IllegalArgumentException("草稿不存在"));
        String normalizedType = normalizeType(type);
        boolean isPaymentProof = isPaymentProofType(normalizedType);

        if (file.getSize() > MAX_FILE_SIZE) {
            throw new IllegalArgumentException("文件大小不能超过200MB");
        }
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
        if (!isPaymentProof && !EVIDENCE_TYPE.equalsIgnoreCase(normalizedType)) {
            String contentType = file.getContentType();
            if (contentType != null && !contentType.contains("pdf")
                    && !contentType.contains("msword")
                    && !contentType.contains("wordprocessingml")
                    && !contentType.contains("spreadsheetml")
                    && !contentType.contains("presentationml")
                    && !contentType.contains("ms-powerpoint")
                    && !contentType.contains("ms-excel")
                    && !contentType.contains("zip")
                    && !contentType.contains("rar")
                    && !contentType.contains("octet-stream")
                    && !contentType.contains("image/")) {
                throw new IllegalArgumentException("不支持的 MIME 类型: " + contentType);
            }
        }

        String fileHash = isPaymentProof ? computeSha256(file) : null;
        validateTypeAndHashRule(normalizedType, fileHash);

        if (isPaymentProof) {
            RegistrationDraftMaterialFile existing = draftMaterialRepository
                    .findFirstByDraftIdAndTypeAndFileHash(draftId, normalizedType, fileHash)
                    .orElse(null);
            if (existing != null) {
                return existing;
            }
        } else if (EVIDENCE_TYPE.equalsIgnoreCase(normalizedType)) {
            List<RegistrationDraftMaterialFile> existing =
                    draftMaterialRepository.findByDraftIdAndType(draftId, normalizedType);
            if (existing.size() >= EVIDENCE_MAX_COUNT) {
                throw new IllegalArgumentException("佐证材料最多上传 " + EVIDENCE_MAX_COUNT + " 个文件");
            }
        } else {
            List<RegistrationDraftMaterialFile> oldFiles =
                    draftMaterialRepository.findByDraftIdAndType(draftId, normalizedType);
            for (RegistrationDraftMaterialFile oldFile : oldFiles) {
                try {
                    fileStorageService.delete(oldFile.getFileUrl());
                } catch (Exception ignored) {
                    // ignore MinIO delete failure
                }
                draftMaterialRepository.delete(oldFile);
            }
        }

        String path = fileStorageService.store("drafts/" + draftId, file);
        RegistrationDraftMaterialFile materialFile = RegistrationDraftMaterialFile.builder()
                .draft(draft)
                .type(normalizedType)
                .fileName(file.getOriginalFilename())
                .fileUrl(path)
                .fileHash(fileHash)
                .uploadedAt(LocalDateTime.now())
                .build();
        try {
            return draftMaterialRepository.save(materialFile);
        } catch (DataIntegrityViolationException e) {
            if (isPaymentProof && fileHash != null) {
                return draftMaterialRepository
                        .findFirstByDraftIdAndTypeAndFileHash(draftId, normalizedType, fileHash)
                        .orElseThrow(() -> e);
            }
            throw e;
        }
    }

    @Transactional
    public void delete(Long materialId) {
        draftMaterialRepository.findById(materialId).ifPresent(material -> {
            try {
                fileStorageService.delete(material.getFileUrl());
            } catch (Exception ignored) {
                // MinIO 删除失败不阻塞
            }
            draftMaterialRepository.delete(material);
        });
    }

    private String getFileExtension(String filename) {
        int lastDotIndex = filename.lastIndexOf('.');
        if (lastDotIndex == -1 || lastDotIndex == filename.length() - 1) {
            return "";
        }
        return filename.substring(lastDotIndex + 1).toLowerCase(Locale.ROOT);
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
        if (REPORT_TYPE.equalsIgnoreCase(type) && !"pdf".equals(ext)) {
            throw new IllegalArgumentException("成果报告书（REPORT）仅支持 PDF 格式，请将文件转换为 PDF 后重新上传");
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
}
