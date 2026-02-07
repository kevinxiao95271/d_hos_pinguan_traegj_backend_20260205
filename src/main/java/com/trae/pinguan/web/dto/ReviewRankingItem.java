package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ReviewRankingItem {
    private Integer rank;
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private String institutionLevel;
    private GroupType groupType;
    private ReviewStage stage;
    private Double avgTotal;
}
