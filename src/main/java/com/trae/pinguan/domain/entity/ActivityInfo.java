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
@Table(name = "activity_infos")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ActivityInfo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "registration_id", unique = true)
    @JsonIgnore
    private Registration registration;

    @Column(name = "registration_id", insertable = false, updatable = false)
    private Long registrationId;

    @Column(nullable = false, length = 120)
    private String theme;

    @Column(nullable = false, length = 120)
    private String keywords;

    @Column(nullable = false, length = 64)
    private String subjectTypeCode;

    @Column(length = 200)
    private String subjectTypeOther;

    @Column(nullable = false, length = 64)
    private String methodCode;

    @Column(length = 200)
    private String methodOther;

    @Column(nullable = false, length = 64)
    private String experienceImproveCode;

    @Column(length = 200)
    private String experienceImproveOther;

    @Column(nullable = false, length = 64)
    private String qualityTopicCode;

    @Column(length = 200)
    private String qualityTopicOther;

    @Column(nullable = false)
    private Integer avgWorkYears;

    @Column(nullable = false)
    private Integer avgAge;

    @Column(nullable = false)
    private Boolean crossDepartment;

    @Column(nullable = false)
    private Boolean relatedToDigitalAi;
}
