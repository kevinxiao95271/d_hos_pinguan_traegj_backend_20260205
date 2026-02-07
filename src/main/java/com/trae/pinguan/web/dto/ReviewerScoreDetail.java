package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ReviewStage;
import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 评委评分详情（单个评委的完整评分记录）
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewerScoreDetail {
    @Schema(description = "评审阶段", example = "BOOK")
    private ReviewStage stage;
    
    @Schema(description = "评委ID", example = "21")
    private Long reviewerId;
    
    @Schema(description = "评委姓名", example = "张三")
    private String reviewerName;
    
    @Schema(description = "评委职称", example = "主任医师")
    private String reviewerTitle;
    
    @Schema(description = "评委机构ID", example = "1")
    private Long reviewerInstitutionId;
    
    @Schema(description = "评委机构名称", example = "浙江大学医学院附属第一医院")
    private String reviewerInstitutionName;
    
    @Schema(description = "评委机构等级", example = "三级甲等")
    private String reviewerInstitutionLevel;
    
    @Schema(description = "各维度评分详情")
    private ScoreBreakdown scores;
    
    @Schema(description = "亮点评语", example = "项目主题明确，改进措施得当，成效显著...")
    private String highlight;
    
    @Schema(description = "改进建议", example = "建议进一步量化成本效益分析...")
    private String weakness;
    
    @Schema(description = "评审提交时间", example = "2026-02-05T14:30:00")
    private LocalDateTime submittedAt;
}
