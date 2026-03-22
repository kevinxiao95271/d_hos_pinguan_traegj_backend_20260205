package com.trae.pinguan.domain.entity;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import java.time.LocalDateTime;
import javax.persistence.*;
import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "scoring_snapshots")
public class ScoringSnapshot {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long competitionId;

    @Column(nullable = false)
    private Long registrationId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private ReviewStage stage;

    @Column(length = 64)
    private String groupCode;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private GroupType groupType;

    /** 项目原始均分（所有评委打分的算术平均，不去极值） */
    private Double rawAvg;

    /** An：该小组所有个人打分的均值（去极值 <65 或 >95 后） */
    private Double groupAvg;

    /** B：全大组所有个人打分的均值（去极值后） */
    private Double overallAvg;

    /** Cn = groupAvg / overallAvg；若无法计算则为 1.0 */
    private Double coefficient;

    /** D = rawAvg / Cn；最终排名依据 */
    private Double adjustedScore;

    private Integer irank;

    @Column(nullable = false)
    private LocalDateTime calculatedAt;
}
