package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.RegistrationStatus;
import com.trae.pinguan.domain.enums.ShortlistOverride;
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

    @Enumerated(EnumType.STRING)
    @Column(length = 16)
    private ShortlistOverride shortlistOverride;

    @Column(length = 200)
    private String shortlistNote;

    /** 现场竞赛日期，如"6.3"、"6.4"、"6.5" */
    @Column(name = "final_session_date", length = 8)
    private String finalSessionDate;

    /** 现场竞赛专场代码，如"综合组-问题解决型专场1" */
    @Column(name = "final_session_code", length = 64)
    private String finalSessionCode;

    /** 专场内上台顺序（1 起始） */
    @Column(name = "final_session_order")
    private Integer finalSessionOrder;

    /** 现场竞赛评分表类型：QCC / NON_QCC / QFD */
    @Column(name = "final_score_form", length = 10)
    private String finalScoreForm;

    /** 项目负责人姓名 */
    @Column(name = "project_leader_name", length = 60)
    private String projectLeaderName;

    /** 项目负责人联系电话 */
    @Column(name = "project_leader_phone", length = 20)
    private String projectLeaderPhone;

    /** 项目负责人职务/职称 */
    @Column(name = "project_leader_title", length = 60)
    private String projectLeaderTitle;
}
