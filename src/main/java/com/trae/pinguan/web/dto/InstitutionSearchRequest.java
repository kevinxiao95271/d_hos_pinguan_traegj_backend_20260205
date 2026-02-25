package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "机构搜索请求")
public class InstitutionSearchRequest {
    
    @Schema(description = "搜索关键词（机构名称、地区）", example = "人民医院")
    private String keyword;
    
    @Schema(description = "地区筛选", example = "杭州市")
    private String region;
    
    @Schema(description = "机构等级", example = "三甲")
    private String level;
    
    @Schema(description = "页码（从0开始）", example = "0")
    private Integer page = 0;
    
    @Schema(description = "每页大小（建议10-50）", example = "20")
    private Integer size = 20;
    
    @Schema(description = "排序字段", example = "name", allowableValues = {"name", "region", "level"})
    private String sortBy = "name";
    
    @Schema(description = "排序方向", example = "ASC", allowableValues = {"ASC", "DESC"})
    private String sortDirection = "ASC";
}
