package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.time.LocalDateTime;
import javax.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "registration_draft_material_files")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class RegistrationDraftMaterialFile {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "draft_id", nullable = false)
    @JsonIgnore
    private RegistrationDraft draft;

    @Column(name = "draft_id", insertable = false, updatable = false)
    private Long draftId;

    @Column(nullable = false, length = 64)
    private String type;

    @Column(name = "file_name", nullable = false, length = 200)
    private String fileName;

    @Column(name = "file_url", nullable = false, length = 300)
    private String fileUrl;

    @Column(name = "file_hash", length = 64)
    private String fileHash;

    @Column(name = "uploaded_at", nullable = false)
    private LocalDateTime uploadedAt;
}
