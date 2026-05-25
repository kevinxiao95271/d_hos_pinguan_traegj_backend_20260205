package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
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
@Table(name = "review_scores")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ReviewScore {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "review_task_id", unique = true)
    @JsonIgnore
    private ReviewTask reviewTask;

    @Column(name = "review_task_id", insertable = false, updatable = false)
    private Long reviewTaskId;

    @Column
    private Double plan;

    @Column
    private Double problem;

    @Column
    private Double action;

    @Column
    private Double success;

    @Column
    private Double review;

    @Column
    private Double operation;

    @Column
    private Double presentation;

    @Column
    private Double total;

    @Column(length = 1000)
    private String highlight;

    @Column(length = 1000)
    private String weakness;

    /** 正式提交时间；草稿状态下为 null */
    @Column
    private LocalDateTime submittedAt;

    /** 第8项得分，非QCC专用（现场表现 10分）；QCC/QFD 置 null */
    @Column(name = "item8")
    private Double item8;

    /** 评分表类型：QCC / NON_QCC / QFD（stage=FINAL 时必填） */
    @Column(name = "score_form", length = 10)
    private String scoreForm;
}
