package com.trae.pinguan.domain.entity;

import com.trae.pinguan.domain.enums.CompetitionStage;
import com.trae.pinguan.domain.enums.CompetitionStatus;
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
@Table(name = "competitions")
public class Competition {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 120)
    private String name;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private CompetitionStage stage;

    private LocalDateTime registerStart;
    private LocalDateTime registerEnd;
    private LocalDateTime bookReviewStart;
    private LocalDateTime bookReviewEnd;
    private LocalDateTime interviewStart;
    private LocalDateTime interviewEnd;
    private LocalDateTime finalStart;
    private LocalDateTime finalEnd;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    /** 赛事状态：DRAFT（草稿）/ ACTIVE（激活，同年唯一） */
    @Builder.Default
    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 16)
    private CompetitionStatus status = CompetitionStatus.DRAFT;

    /** 基层组分组前缀，默认 A */
    @Column(name = "basic_group_prefix", length = 8)
    private String basicGroupPrefix = "A";

    /** 综合组分组前缀，默认 B */
    @Column(name = "comprehensive_group_prefix", length = 8)
    private String comprehensiveGroupPrefix = "B";

    /** 进阶组分组前缀，默认 C */
    @Column(name = "advanced_group_prefix", length = 8)
    private String advancedGroupPrefix = "C";
}
