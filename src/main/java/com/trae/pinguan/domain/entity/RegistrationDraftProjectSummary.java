package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
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
@Table(name = "registration_draft_project_summaries")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class RegistrationDraftProjectSummary {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "draft_id", nullable = false, unique = true)
    @JsonIgnore
    private RegistrationDraft draft;

    @Column(name = "draft_id", insertable = false, updatable = false)
    private Long draftId;

    @Column(nullable = false, length = 200)
    private String theme;

    @Column(nullable = false, length = 1000)
    private String plan;

    @Column(nullable = false, length = 1000)
    private String problem;

    @Column(nullable = false, length = 1000)
    private String action;

    @Column(nullable = false, length = 1000)
    private String success;

    @Column(nullable = false, length = 1000)
    private String discussion;

    @Column(length = 1000)
    private String operation;

    @Column(length = 1000)
    private String presentation;
}
