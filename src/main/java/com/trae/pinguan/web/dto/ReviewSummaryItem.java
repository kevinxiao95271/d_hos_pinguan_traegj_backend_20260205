package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ReviewSummaryItem {
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private GroupType groupType;
    private ReviewStage stage;
    private Double avgTotal;
    private Integer scoresCount;
}
