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

    @Column(nullable = false)
    private Double plan;

    @Column(nullable = false)
    private Double problem;

    @Column(nullable = false)
    private Double action;

    @Column(nullable = false)
    private Double success;

    @Column(nullable = false)
    private Double review;

    @Column(nullable = false)
    private Double operation;

    @Column(nullable = false)
    private Double presentation;

    @Column(nullable = false)
    private Double total;

    @Column(nullable = false, length = 500)
    private String highlight;

    @Column(nullable = false, length = 500)
    private String weakness;

    @Column(nullable = false)
    private LocalDateTime submittedAt;
}
