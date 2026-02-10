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
    @Schema(example = "20.0")
    private Double plan;
    @Min(0)
    @Max(100)
    @Schema(example = "20.0")
    private Double problem;
    @Min(0)
    @Max(100)
    @Schema(example = "20.0")
    private Double action;
    @Min(0)
    @Max(100)
    @Schema(example = "15.0")
    private Double success;
    @Min(0)
    @Max(100)
    @Schema(example = "10.0")
    private Double review;
    @Min(0)
    @Max(100)
    @Schema(example = "10.0")
    private Double operation;
    @Min(0)
    @Max(100)
    @Schema(example = "5.0")
    private Double presentation;
    @NotBlank
    @Schema(example = "结构清晰")
    private String highlight;
    @NotBlank
    @Schema(example = "细节可加强")
    private String weakness;
}
