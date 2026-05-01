package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;
import java.util.List;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@Schema(description = "得分列表条目（书审 / 面谈通用）")
public class ScoreListItem {

    @Schema(description = "报名 ID")
    private Long registrationId;

    @Schema(description = "项目名称")
    private String projectName;

    @Schema(description = "参赛机构名称")
    private String institutionName;

    @Schema(description = "机构等级，如：三级甲等")
    private String institutionLevel;

    @Schema(description = "组别类型：BASIC / COMPREHENSIVE / ADVANCED")
    private GroupType groupType;

    @Schema(description = "小组代码，如：A1 / C2")
    private String groupCode;

    @Schema(description = "阶段：BOOK / INTERVIEW")
    private ReviewStage stage;

    @Schema(description = "评委打分明细列表")
    private List<ReviewerScoreDetail> reviewerScores;

    @Schema(description = "已打分评委数")
    private int scoredCount;

    @Schema(description = "分配评委总数（含未打分）")
    private int totalReviewers;

    @Schema(description = "所有评委总分均值（仅统计已打分）")
    private Double avgTotal;

    // ── 每位评委的打分明细 ──────────────────────────────

    @Data
    @Builder
    @Schema(description = "单个评委的打分明细")
    public static class ReviewerScoreDetail {

        @Schema(description = "评审任务 ID（驳回操作传此字段）")
        private Long reviewTaskId;

        @Schema(description = "评委 ID")
        private Long reviewerId;

        @Schema(description = "评委姓名")
        private String reviewerName;

        @Schema(description = "打分状态：PENDING（待评审）/ DRAFT（草稿中）/ SCORED（已提交）/ RETURNED（已退回）/ RECUSED（已规避）")
        private String status;

        @Schema(description = "打分提交时间")
        private LocalDateTime submittedAt;

        // ── 书审维度（stage=BOOK 时有值）──────────────
        @Schema(description = "【书审】计划拟定")
        private Double plan;

        @Schema(description = "【书审】问题解析")
        private Double problem;

        @Schema(description = "【书审】对策拟定与实施")
        private Double action;

        @Schema(description = "【书审】成果")
        private Double success;

        @Schema(description = "【书审】检讨与改进")
        private Double review;

        @Schema(description = "【书审】活动运作")
        private Double operation;

        @Schema(description = "【书审】报告呈现")
        private Double presentation;

        // ── 面谈维度（stage=INTERVIEW 时有值）──────────
        @Schema(description = "【面谈】选题")
        private Double topic;

        @Schema(description = "【面谈】改善过程确实性")
        private Double process;

        @Schema(description = "【面谈】整体运作")
        private Double interviewOperation;

        @Schema(description = "【面谈】改善成果")
        private Double result;

        // ── 通用 ────────────────────────────────────
        @Schema(description = "总分")
        private Double total;

        @Schema(description = "亮点意见")
        private String highlight;

        @Schema(description = "不足意见")
        private String weakness;
    }
}
