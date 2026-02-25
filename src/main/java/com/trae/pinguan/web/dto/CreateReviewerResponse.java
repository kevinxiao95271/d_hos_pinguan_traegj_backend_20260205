package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "创建评委账号响应")
public class CreateReviewerResponse {
    
    @Schema(description = "用户ID")
    private Long userId;
    
    @Schema(description = "手机号")
    private String phone;
    
    @Schema(description = "姓名")
    private String name;
    
    @Schema(description = "初始密码（请通知评委尽快修改）")
    private String initialPassword;
    
    @Schema(description = "机构名称")
    private String institutionName;
}
