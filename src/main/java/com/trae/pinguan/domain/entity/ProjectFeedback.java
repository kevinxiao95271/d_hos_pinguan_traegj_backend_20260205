package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.trae.pinguan.domain.enums.ReviewStage;
import java.time.LocalDateTime;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.EnumType;
import javax.persistence.Enumerated;
import javax.persistence.FetchType;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.Lob;
import javax.persistence.ManyToOne;
import javax.persistence.Table;
import javax.persistence.UniqueConstraint;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "project_feedbacks",
        uniqueConstraints = @UniqueConstraint(name = "uk_project_feedback_registration_stage",
                columnNames = {"registration_id", "stage"}))
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ProjectFeedback {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "registration_id", nullable = false)
    @JsonIgnore
    private Registration registration;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private ReviewStage stage;

    @Lob
    @Column(name = "source_highlight")
    private String sourceHighlight;

    @Lob
    @Column(name = "source_weakness")
    private String sourceWeakness;

    @Lob
    @Column(name = "edited_highlight")
    private String editedHighlight;

    @Lob
    @Column(name = "edited_weakness")
    private String editedWeakness;

    @Column(nullable = false)
    private boolean published;

    @Column(name = "updated_by_id")
    private Long updatedById;

    @Column(name = "published_by_id")
    private Long publishedById;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @Column
    private LocalDateTime publishedAt;
}
