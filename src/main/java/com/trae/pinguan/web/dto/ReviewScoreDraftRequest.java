package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.Max;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
@Schema(description = "书审评分草稿保存（字段均可为空，仅更新已传入的字段）")
public class ReviewScoreDraftRequest {

    @NotNull(message = "评审任务ID不能为空")
    private Long reviewTaskId;

    @Min(0) @Max(100)
    private Double plan;

    @Min(0) @Max(100)
    private Double problem;

    @Min(0) @Max(100)
    private Double action;

    @Min(0) @Max(100)
    private Double success;

    @Min(0) @Max(100)
    private Double review;

    @Min(0) @Max(100)
    private Double operation;

    @Min(0) @Max(100)
    private Double presentation;

    @Size(max = 1000)
    private String highlight;

    @Size(max = 1000)
    private String weakness;
}
