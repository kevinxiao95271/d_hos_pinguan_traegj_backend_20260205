package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MyCompetitionItem {
    private Long competitionId;
    private String competitionName;

    @Schema(description = "赛事年度（取自赛事 createdAt 年份）")
    private Integer year;

    @Schema(description = "该届已提交/正式报名条数（不含草稿表）")
    private int registrationCount;

    @Schema(description = "该届草稿条数")
    private int draftCount;

    @Schema(description = "是否为当前默认届（ID 最大的赛事，与登录 currentCompetitionId 一致）")
    private boolean current;
}
