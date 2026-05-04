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

    @Schema(description = "纯面谈模式：true 时进阶组跳过书审合分，直接走通用系数路径，快照存入 INTERVIEW_ONLY stage，与 INTERVIEW 快照完全隔离")
    private boolean interviewOnly = false;
}
