package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.trae.pinguan.domain.enums.ApprovalStatus;
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
@Table(name = "institution_update_requests")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class InstitutionUpdateRequest {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "institution_id")
    @JsonIgnore
    private Institution institution;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "submitter_id")
    @JsonIgnore
    private UserAccount submitter;

    @Column(length = 200)
    private String newName;

    @Column(length = 64)
    private String newCode;

    @Column(length = 32)
    private String newUscc;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private ApprovalStatus status;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    private LocalDateTime reviewedAt;
}
