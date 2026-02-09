package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 机构信息DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InstitutionInfo {
    @Schema(description = "机构ID", example = "1")
    private Long id;
    
    @Schema(description = "医疗机构名称", example = "浙江大学医学院附属第一医院")
    private String name;
    
    @Schema(description = "机构编号", example = "33010001")
    private String code;
    
    @Schema(description = "统一社会信用代码", example = "12330000470093469F")
    private String uscc;
    
    @Schema(description = "地区", example = "浙江省杭州市")
    private String region;
    
    @Schema(description = "机构等级", example = "三级甲等")
    private String level;
}
