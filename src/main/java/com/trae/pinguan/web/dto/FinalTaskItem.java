package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@Schema(description = "评委现场评分任务")
public class FinalTaskItem {

    @Schema(description = "任务 ID")
    private Long taskId;

    @Schema(description = "报名 ID")
    private Long registrationId;

    @Schema(description = "专场代码")
    private String sessionCode;

    @Schema(description = "专场内顺序")
    private Integer sessionOrder;

    @Schema(description = "项目名称")
    private String projectName;

    @Schema(description = "机构名称")
    private String institutionName;

    @Schema(description = "组别代码")
    private String groupCode;

    @Schema(description = "评分表类型：QCC / NON_QCC / QFD")
    private String scoreForm;

    @Schema(description = "评审专家 ID")
    private Long reviewerId;

    @Schema(description = "评审专家姓名")
    private String reviewerName;

    @Schema(description = "评审专家手机号")
    private String reviewerPhone;

    @Schema(description = "任务状态：PENDING / DRAFT / SCORED / RECUSED")
    private String status;

    @Schema(description = "合计得分（已提交）")
    private Double total;

    @Schema(description = "结构化评分明细，按评分表翻译后的分项列表（含标签、满分、实际得分）")
    private List<FinalScoreItem> scoreItems;

    @Schema(description = "已保存的草稿原始评分（供评委端回显用）")
    private FinalScoreRequest draftScore;
}
