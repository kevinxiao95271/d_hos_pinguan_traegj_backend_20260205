package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.Max;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
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
    @Size(max = 1000, message = "亮点不能超过1000字")
    @Schema(example = "结构清晰，思路新颖")
    private String highlight;

    @Size(max = 1000, message = "建议不能超过1000字")
    @Schema(example = "细节可加强")
    private String weakness;
}
