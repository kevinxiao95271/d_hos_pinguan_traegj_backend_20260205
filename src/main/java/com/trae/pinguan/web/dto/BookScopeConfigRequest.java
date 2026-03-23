package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
@Schema(description = "书审阶段入围范围配置请求")
public class BookScopeConfigRequest {

    @NotNull
    @Schema(description = "入围范围模式：PER_GROUP=各组独立配置；UNIFIED=全书审阶段统一比例",
            allowableValues = {"PER_GROUP", "UNIFIED"})
    private String scope;

    @Schema(description = "UNIFIED模式下的计算方式：RATIO=按比例；COUNT=取前N名（scope=UNIFIED时必填）",
            allowableValues = {"RATIO", "COUNT"})
    private String unifiedMode;

    @Schema(description = "UNIFIED模式下的值：RATIO时为小数（如0.55），COUNT时为整数（如30）（scope=UNIFIED时必填）")
    private Double unifiedValue;
}
