package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.RegistrationStatus;
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
@Table(name = "registrations")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Registration {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "competition_id")
    @JsonIgnore
    private Competition competition;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "institution_id")
    @JsonIgnore
    private Institution institution;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "applicant_id")
    @JsonIgnore
    private UserAccount applicant;

    @Column(nullable = false, length = 120)
    private String projectName;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private GroupType groupType;

    @Column(length = 64)
    private String groupCode;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private RegistrationStatus status;

    private LocalDateTime submittedAt;

    @Column(nullable = false)
    private LocalDateTime createdAt;
}
