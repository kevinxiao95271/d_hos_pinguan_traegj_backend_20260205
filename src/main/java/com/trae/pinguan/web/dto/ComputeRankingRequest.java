package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
@Schema(description = "触发排名计算请求")
public class ComputeRankingRequest {

    @NotNull
    @Schema(description = "赛事ID")
    private Long competitionId;

    @NotNull
    @Schema(description = "评审阶段：BOOK/INTERVIEW/FINAL")
    private ReviewStage stage;

    @Schema(description = "组别（不传则计算全部组别）")
    private GroupType groupType;
}
