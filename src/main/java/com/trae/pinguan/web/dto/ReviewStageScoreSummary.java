package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ReviewStage;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ReviewStageScoreSummary {
    private ReviewStage stage;
    private int taskCount;
    private int scoredCount;
    private Double avgPlan;
    private Double avgProblem;
    private Double avgAction;
    private Double avgSuccess;
    private Double avgReview;
    private Double avgOperation;
    private Double avgPresentation;
    private Double avgTotal;
    private List<String> highlights;
    private List<String> weaknesses;
}
