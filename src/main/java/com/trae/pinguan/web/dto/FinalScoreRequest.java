package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.DecimalMax;
import javax.validation.constraints.DecimalMin;
import lombok.Data;

@Data
@Schema(description = "现场评分提交请求")
public class FinalScoreRequest {

    @Schema(description = "评分表类型：QCC / NON_QCC / QFD", required = true, example = "QCC")
    private String scoreForm;

    // ── QCC 7项 / 非QCC 前7项 / QFD 前5项 ────────────────────────────────

    @Schema(description = "第1项得分（QCC:计划10 / 非QCC:选题15 / QFD:圈活动特征15）")
    @DecimalMin("0") @DecimalMax("30")
    private Double plan;

    @Schema(description = "第2项得分（QCC:项目结构15 / 非QCC:原因分析10 / QFD:课题明确化25）")
    @DecimalMin("0") @DecimalMax("30")
    private Double problem;

    @Schema(description = "第3项得分（QCC:对策行动15 / 非QCC:计划10 / QFD:方策拟定25）")
    @DecimalMin("0") @DecimalMax("30")
    private Double action;

    @Schema(description = "第4项得分（QCC:成果表现20 / 非QCC:实施20 / QFD:执行力成果25）")
    @DecimalMin("0") @DecimalMax("30")
    private Double success;

    @Schema(description = "第5项得分（QCC:查验5 / 非QCC:成果表现10 / QFD:现场发表10）")
    @DecimalMin("0") @DecimalMax("30")
    private Double review;

    @Schema(description = "第6项得分（QCC:整体运作15 / 非QCC:检讨10）；QFD 不用")
    @DecimalMin("0") @DecimalMax("30")
    private Double operation;

    @Schema(description = "第7项得分（QCC:现场表现20 / 非QCC:整体运作15）；QFD 不用")
    @DecimalMin("0") @DecimalMax("30")
    private Double presentation;

    @Schema(description = "第8项得分（非QCC专用：现场表现10）；QCC/QFD 不用")
    @DecimalMin("0") @DecimalMax("30")
    private Double item8;

    @Schema(description = "合计分（前端传入，后端也会重新校验）")
    private Double total;

    @Schema(description = "亮点意见", maxLength = 1000)
    private String highlight;

    @Schema(description = "不足意见", maxLength = 1000)
    private String weakness;
}
