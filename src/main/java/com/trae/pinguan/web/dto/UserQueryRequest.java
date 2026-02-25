package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.RoleType;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "用户查询请求")
public class UserQueryRequest {
    
    @Schema(description = "手机号（模糊搜索）", example = "138")
    private String phone;
    
    @Schema(description = "姓名（模糊搜索）", example = "张")
    private String name;
    
    @Schema(description = "角色筛选", example = "CONTESTANT")
    private RoleType role;
    
    @Schema(description = "机构ID筛选", example = "123")
    private Long institutionId;
    
    @Schema(description = "启用状态（true=启用，false=禁用）", example = "true")
    private Boolean enabled;
    
    @Schema(description = "页码（从0开始）", example = "0")
    private Integer page = 0;
    
    @Schema(description = "每页大小", example = "20")
    private Integer size = 20;
}
