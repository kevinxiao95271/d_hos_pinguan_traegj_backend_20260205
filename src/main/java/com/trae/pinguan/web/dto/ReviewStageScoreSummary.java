package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ReviewStage;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewStageScoreSummary {
    private ReviewStage stage;
    private int taskCount;
    private int scoredCount;
    // 书审维度（stage=BOOK 时有值）
    private Double avgPlan;
    private Double avgProblem;
    private Double avgAction;
    private Double avgSuccess;
    private Double avgReview;
    private Double avgOperation;
    private Double avgPresentation;

    // 面谈维度（stage=INTERVIEW 时有值）
    private Double avgTopic;
    private Double avgProcess;
    private Double avgInterviewOperation;
    private Double avgResult;

    private Double avgTotal;
    private List<String> highlights;
    private List<String> weaknesses;
}
