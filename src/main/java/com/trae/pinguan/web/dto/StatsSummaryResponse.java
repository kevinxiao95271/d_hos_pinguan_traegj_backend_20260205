package com.trae.pinguan.web.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import java.util.Map;

@Data
@AllArgsConstructor
public class StatsSummaryResponse {
    private Long competitionId;
    private String competitionName;
    private Integer registrationCount;
    private Integer toolTypeCount;
    private Integer reviewerCount;
    private Integer reviewerInstitutionCount;
    private Integer bookReviewTaskCount;
    private Integer bookReviewUnscoredCount;
    private Map<String, Integer> regionCounts;
    private Map<String, Integer> subjectTypeCounts;
    private Map<String, Integer> methodCounts;
    private Map<String, Integer> leaderTitleCounts;
    private Double avgPlan;
    private Double avgProblem;
    private Double avgAction;
    private Double avgSuccess;
    private Double avgReview;
    private Double avgOperation;
    private Double avgPresentation;
}
