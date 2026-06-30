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

    @Schema(description = "现场竞赛直接均分")
    private Double trimmedAvg;

    @Schema(description = "现场均分（同 trimmedAvg，统一命名别名）")
    private Double finalAvg;

    @Schema(description = "书审D值（BASIC/COMPREHENSIVE）或书审+面谈合并D（ADVANCED），向后兼容保留")
    private Double bookReviewScore;

    @Schema(description = "书审标化D值（BASIC/COMPREHENSIVE 及 ADVANCED 三阶段均有值）")
    private Double bookScoreD;

    @Schema(description = "面谈标化D值（ADVANCED 有值；BASIC/COMPREHENSIVE 为 null）")
    private Double interviewScoreD;

    @Schema(description = "书审D权重：BASIC/COMPREHENSIVE=0.4，ADVANCED 三阶段=0.3")
    private Double bookWeight;

    @Schema(description = "面谈D权重：ADVANCED 三阶段=0.4，其他为 null")
    private Double interviewWeight;

    @Schema(description = "现场均分权重：BASIC/COMPREHENSIVE=0.6，ADVANCED 三阶段=0.3")
    private Double finalWeight;

    @Schema(description = "得分算式字符串，如 82.50 x 40% + 89.10 x 60% = 86.46")
    private String scoreFormula;

    @Schema(description = "综合总分 = 书审D*40% + 现场均分*60%")
    private Double totalScore;

    @Schema(description = "专场内总分排名")
    private Integer totalRank;

    @Schema(description = "奖项等级：GOLD / SILVER / BRONZE，未入奖为 null")
    private String awardLevel;

    @Schema(description = "说明备注")
    private String note;
}
