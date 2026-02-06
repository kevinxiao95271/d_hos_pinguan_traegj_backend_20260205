package com.trae.pinguan.domain.entity;

import com.trae.pinguan.domain.enums.CompetitionStage;
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
}
