package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ReviewStage;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ReviewFeedbackItem {
    @Schema(example = "101")
    private Long registrationId;
    @Schema(example = "项目A")
    private String projectName;
    @Schema(example = "某医院")
    private String institutionName;
    @Schema(example = "BOOK")
    private ReviewStage stage;
    @Schema(example = "12")
    private Long reviewerId;
    @Schema(example = "张评委")
    private String reviewerName;
    @Schema(example = "85")
    private Integer total;
    @Schema(example = "结构清晰")
    private String highlight;
    @Schema(example = "细节可加强")
    private String weakness;
}
