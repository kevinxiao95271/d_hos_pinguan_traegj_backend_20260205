package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
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
public class ScoreExportRow {
    private Integer irank;
    private GroupType groupType;
    private String groupCode;
    private ReviewStage stage;
    private Long registrationId;
    private String projectName;
    private String institutionName;
    /** 各评委的总分，顺序对应评审1/评审2/... */
    private List<Double> reviewerScores;
    private Double rawAvg;
    private Double groupAvg;
    private Double overallAvg;
    private Double coefficient;
    private Double adjustedScore;
}
