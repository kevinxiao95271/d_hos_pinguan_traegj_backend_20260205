package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.RegistrationStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class AutoGroupRequest {
    @NotNull
    @Schema(example = "21", description = "竞赛ID")
    private Long competitionId;

    @Schema(example = "APPROVED", description = "筛选报名状态（可选，不填则处理所有状态）")
    private RegistrationStatus status;

    @Schema(example = "20", description = "最小分组大小（默认20）")
    private Integer minGroupSize = 20;

    @Schema(example = "31", description = "最大分组大小（默认31）")
    private Integer maxGroupSize = 31;

    @Schema(example = "2.5", description = "分组大小标准差上限（默认2.5）")
    private Double maxStdDev = 2.5;

    @Schema(example = "2", description = "同机构项目最多散落分组数（默认2，推荐1-3）")
    private Integer maxInstitutionSpread = 2;
}

