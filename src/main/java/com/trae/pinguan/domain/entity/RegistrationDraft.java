package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.trae.pinguan.domain.enums.GroupType;
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
@Table(name = "registration_drafts")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class RegistrationDraft {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "competition_id", nullable = false)
    @JsonIgnore
    private Competition competition;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "institution_id", nullable = false)
    @JsonIgnore
    private Institution institution;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "applicant_id", nullable = false)
    @JsonIgnore
    private UserAccount applicant;

    @Column(name = "project_name", nullable = false, length = 120)
    private String projectName;

    @Enumerated(EnumType.STRING)
    @Column(name = "group_type", nullable = false, length = 32)
    private GroupType groupType;

    @Column(name = "project_leader_name", length = 60)
    private String projectLeaderName;

    @Column(name = "project_leader_phone", length = 20)
    private String projectLeaderPhone;

    @Column(name = "project_leader_title", length = 60)
    private String projectLeaderTitle;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
}
