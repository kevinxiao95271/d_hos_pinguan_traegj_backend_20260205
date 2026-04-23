package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.time.LocalDateTime;
import javax.persistence.*;
import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "interview_scores")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class InterviewScore {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "review_task_id", unique = true)
    @JsonIgnore
    private ReviewTask reviewTask;

    @Column(name = "review_task_id", insertable = false, updatable = false)
    private Long reviewTaskId;

    /** 选题：迫切性、实用性、可行性（满分10） */
    @Column
    private Double topic;

    /** 改善过程的确实性（满分40） */
    @Column
    private Double process;

    /** 整体运作（满分20） */
    @Column
    private Double operation;

    /** 改善成果（满分30） */
    @Column
    private Double result;

    /** 合计（满分100，= topic+process+operation+result） */
    @Column
    private Double total;

    /** 正式提交时间；草稿状态下为 null */
    @Column
    private LocalDateTime submittedAt;
}
