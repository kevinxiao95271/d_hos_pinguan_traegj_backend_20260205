package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.RegistrationStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class AutoGroupRequest {
    @NotNull
    @Schema(example = "21")
    private Long competitionId;

    @Schema(description = "组别类型（可选）：BASIC-基层组, COMPREHENSIVE-综合组, ADVANCED-进阶组。"
            + "不指定时对所有组别执行分组，分组前缀由系统自动推导", example = "BASIC")
    private GroupType groupType;

    @Schema(description = "分组前缀（可选）。不传时由系统根据 groupType 及赛事配置自动推导；"
            + "传入时须与 groupType 一致且为该赛事配置的有效前缀",
            example = "A")
    private String groupPrefix;

    @NotNull
    @Min(1)
    @Schema(example = "6")
    private Integer groupSize;

    @Schema(example = "APPROVED")
    private RegistrationStatus status;
}
