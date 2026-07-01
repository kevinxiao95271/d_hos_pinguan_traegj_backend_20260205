package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.RegistrationDraftMaterialFile;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RegistrationDraftMaterialFileRepository extends JpaRepository<RegistrationDraftMaterialFile, Long> {
    List<RegistrationDraftMaterialFile> findByDraftId(Long draftId);
    List<RegistrationDraftMaterialFile> findByDraftIdAndType(Long draftId, String type);
    Optional<RegistrationDraftMaterialFile> findFirstByDraftIdAndTypeAndFileHash(
            Long draftId, String type, String fileHash);
    void deleteByDraftId(Long draftId);
}
