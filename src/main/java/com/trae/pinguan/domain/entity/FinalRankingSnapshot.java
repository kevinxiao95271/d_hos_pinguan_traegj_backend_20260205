package com.trae.pinguan.domain.entity;

import java.time.LocalDateTime;
import javax.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 现场竞赛排名快照。
 * 每次执行"计算排名"接口时，先清空当前竞赛的旧快照，再重新写入。
 * 与 scoring_snapshots 表完全独立，不受书审/面试系数逻辑影响。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "final_ranking_snapshots",
        indexes = {
                @Index(name = "idx_frs_comp_session", columnList = "competition_id, session_code"),
                @Index(name = "idx_frs_comp_reg",     columnList = "competition_id, registration_id", unique = true)
        })
public class FinalRankingSnapshot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "competition_id", nullable = false)
    private Long competitionId;

    @Column(name = "registration_id", nullable = false)
    private Long registrationId;

    /** 日期，如 6.3 / 6.4 / 6.5（来自 registrations.final_session_date） */
    @Column(name = "session_date", length = 8)
    private String sessionDate;

    /** 专场代码（即 registrations.final_session_code） */
    @Column(name = "session_code", nullable = false, length = 64)
    private String sessionCode;

    /** 专场内上台顺序（来自 registrations.final_session_order） */
    @Column(name = "session_order")
    private Integer sessionOrder;

    /** 评分表类型（QCC / NON_QCC / QFD） */
    @Column(name = "score_form", length = 10)
    private String scoreForm;

    /** 参与计算的评委打分条数（去极值后） */
    @Column(name = "judge_score_count")
    private Integer judgeScoreCount;

    /**
     * 会场级去极值：该会场所有打分池中被去掉的最高分值。
     * 若人数不足未去极值则为 null。
     */
    @Column(name = "session_removed_max")
    private Double sessionRemovedMax;

    /**
     * 会场级去极值：该会场所有打分池中被去掉的最低分值。
     */
    @Column(name = "session_removed_min")
    private Double sessionRemovedMin;

    /** 去极值后该项目所有评委打分的平均分（最终排名依据） */
    @Column(name = "trimmed_avg")
    private Double trimmedAvg;

    /** 专场内排名（1 名最高） */
    @Column(name = "session_rank")
    private Integer sessionRank;

    @Column(name = "calculated_at", nullable = false)
    private LocalDateTime calculatedAt;
}
