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
@Table(name = "registration_draft_activity_infos")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class RegistrationDraftActivityInfo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "draft_id", nullable = false, unique = true)
    @JsonIgnore
    private RegistrationDraft draft;

    @Column(name = "draft_id", insertable = false, updatable = false)
    private Long draftId;

    @Column(nullable = false, length = 120)
    private String theme;

    @Column(nullable = false, length = 120)
    private String keywords;

    @Column(name = "subject_type_code", nullable = false, length = 64)
    private String subjectTypeCode;

    @Column(name = "subject_type_other", length = 200)
    private String subjectTypeOther;

    @Column(name = "method_code", nullable = false, length = 64)
    private String methodCode;

    @Column(name = "method_other", length = 200)
    private String methodOther;

    @Column(name = "experience_improve_code", nullable = false, length = 64)
    private String experienceImproveCode;

    @Column(name = "experience_improve_other", length = 200)
    private String experienceImproveOther;

    @Column(name = "quality_topic_code", nullable = false, length = 64)
    private String qualityTopicCode;

    @Column(name = "quality_topic_other", length = 200)
    private String qualityTopicOther;

    @Column(name = "avg_work_years", nullable = false)
    private Integer avgWorkYears;

    @Column(name = "avg_age", nullable = false)
    private Integer avgAge;

    @Column(name = "cross_department", nullable = false)
    private Boolean crossDepartment;

    @Column(name = "related_to_digital_ai", nullable = false)
    private Boolean relatedToDigitalAi;
}
