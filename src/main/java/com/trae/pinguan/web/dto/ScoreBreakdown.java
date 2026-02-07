package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 评分详情（7个维度 + 总分）
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScoreBreakdown {
    @Schema(description = "计划维度得分", example = "18")
    private Integer plan;
    
    @Schema(description = "问题维度得分", example = "17")
    private Integer problem;
    
    @Schema(description = "行动维度得分", example = "19")
    private Integer action;
    
    @Schema(description = "成效维度得分", example = "18")
    private Integer success;
    
    @Schema(description = "回顾维度得分", example = "16")
    private Integer review;
    
    @Schema(description = "运作维度得分", example = "0")
    private Integer operation;
    
    @Schema(description = "展示维度得分", example = "0")
    private Integer presentation;
    
    @Schema(description = "总分", example = "88")
    private Integer total;
}
