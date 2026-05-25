package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@Schema(description = "现场竞赛排名条目")
public class FinalRankingItem {

    @Schema(description = "日期，如 6.3 / 6.4 / 6.5")
    private String sessionDate;

    @Schema(description = "专场代码")
    private String sessionCode;

    @Schema(description = "专场内排名")
    private Integer rank;

    @Schema(description = "报名 ID")
    private Long registrationId;

    @Schema(description = "专场内上台顺序")
    private Integer sessionOrder;

    @Schema(description = "项目名称")
    private String projectName;

    @Schema(description = "机构名称")
    private String institutionName;

    @Schema(description = "评分表类型：QCC / NON_QCC / QFD")
    private String scoreForm;

    @Schema(description = "参与计算的评委数")
    private int judgeCount;

    @Schema(description = "去极值后均分（最终排名依据）")
    private Double trimmedAvg;

    @Schema(description = "说明：是否因人数不足未去极值")
    private String note;
}
