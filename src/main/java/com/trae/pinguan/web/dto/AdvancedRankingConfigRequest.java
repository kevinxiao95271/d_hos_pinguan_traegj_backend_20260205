package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.DecimalMax;
import javax.validation.constraints.DecimalMin;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
@Schema(description = "进阶组合分配置请求")
public class AdvancedRankingConfigRequest {

    @NotNull
    @DecimalMin("0.0") @DecimalMax("1.0")
    @Schema(description = "书审权重（0~1，如 0.4 表示 40%）")
    private Double bookWeight;

    @NotNull
    @DecimalMin("0.0") @DecimalMax("1.0")
    @Schema(description = "面谈权重（0~1，如 0.6 表示 60%）")
    private Double interviewWeight;

    @NotNull
    @Schema(description = "调整模式：ADJUST_THEN_WEIGHT=各阶段分别系数调整后加权；WEIGHT_THEN_ADJUST=先加权再统一做系数调整",
            allowableValues = {"ADJUST_THEN_WEIGHT", "WEIGHT_THEN_ADJUST"})
    private String rankingMode;
}
