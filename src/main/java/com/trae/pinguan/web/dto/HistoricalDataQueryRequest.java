package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 历史数据查询请求
 */
@Data
@Schema(description = "历史数据查询请求")
public class HistoricalDataQueryRequest {
    
    @Schema(description = "地区关键词（从机构地址中模糊匹配）")
    private String region;
    
    @Schema(description = "组别（competition_group）")
    private String competitionGroup;
    
    @Schema(description = "品管工具/圈名（circle_name）")
    private String circleName;
    
    @Schema(description = "入围状态（data_status）")
    private String dataStatus;
    
    @Schema(description = "医院名称（institution_name）")
    private String institutionName;
    
    @Schema(description = "项目名称（project_name）")
    private String projectName;
    
    @Schema(description = "年份")
    private String year;
    
    @Schema(description = "页码（从0开始）", example = "0")
    private Integer page = 0;
    
    @Schema(description = "每页大小", example = "20")
    private Integer size = 20;
    
    @Schema(description = "排序字段", example = "id")
    private String sortBy = "id";
    
    @Schema(description = "排序方向（ASC/DESC）", example = "DESC")
    private String sortDirection = "DESC";
}
