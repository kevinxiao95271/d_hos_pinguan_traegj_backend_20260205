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

    @Column(nullable = false)
    private Integer plan;

    @Column(nullable = false)
    private Integer problem;

    @Column(nullable = false)
    private Integer action;

    @Column(nullable = false)
    private Integer success;

    @Column(nullable = false)
    private Integer review;

    @Column(nullable = false)
    private Integer operation;

    @Column(nullable = false)
    private Integer presentation;

    @Column(nullable = false)
    private Integer total;

    @Column(nullable = false, length = 500)
    private String highlight;

    @Column(nullable = false, length = 500)
    private String weakness;

    @Column(nullable = false)
    private LocalDateTime submittedAt;
}
