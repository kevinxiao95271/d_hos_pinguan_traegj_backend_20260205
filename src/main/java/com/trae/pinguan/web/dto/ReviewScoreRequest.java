package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.Max;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class ReviewScoreRequest {
    @NotNull
    @Schema(example = "101")
    private Long reviewTaskId;
    @Min(0)
    @Max(100)
    @Schema(example = "20")
    private Integer plan;
    @Min(0)
    @Max(100)
    @Schema(example = "20")
    private Integer problem;
    @Min(0)
    @Max(100)
    @Schema(example = "20")
    private Integer action;
    @Min(0)
    @Max(100)
    @Schema(example = "15")
    private Integer success;
    @Min(0)
    @Max(100)
    @Schema(example = "10")
    private Integer review;
    @Min(0)
    @Max(100)
    @Schema(example = "10")
    private Integer operation;
    @Min(0)
    @Max(100)
    @Schema(example = "5")
    private Integer presentation;
    @NotBlank
    @Schema(example = "结构清晰")
    private String highlight;
    @NotBlank
    @Schema(example = "细节可加强")
    private String weakness;
}
