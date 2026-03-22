package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
@Schema(description = "入围配置请求")
public class ShortlistConfigRequest {

    @NotNull
    @Schema(description = "组别：BASIC/COMPREHENSIVE/ADVANCED")
    private GroupType groupType;

    @NotNull
    @Schema(description = "入围模式：RATIO（按比例）或 COUNT（取前N名）", allowableValues = {"RATIO", "COUNT"})
    private String mode;

    @NotNull
    @Schema(description = "入围值：RATIO时为小数（如0.55表示55%），COUNT时为整数（如30）")
    private Double value;
}
