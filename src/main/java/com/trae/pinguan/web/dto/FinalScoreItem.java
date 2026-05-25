package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
@Schema(description = "单项评分明细（含标签和满分）")
public class FinalScoreItem {

    @Schema(description = "分项名称，如 计划 / 项目结构 / 成果表现")
    private String label;

    @Schema(description = "该项满分值，如 10 / 15 / 20")
    private int maxScore;

    @Schema(description = "实际得分，未打分则为 null")
    private Double score;
}
