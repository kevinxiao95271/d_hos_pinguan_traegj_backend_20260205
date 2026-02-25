package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
@Schema(description = "修改密码请求")
public class ChangePasswordRequest {
    
    @NotBlank(message = "旧密码不能为空")
    @Schema(description = "旧密码", example = "oldPassword123", required = true)
    private String oldPassword;
    
    @NotBlank(message = "新密码不能为空")
    @Size(min = 6, max = 20, message = "密码长度必须在6-20位之间")
    @Schema(description = "新密码（6-20位）", example = "newPassword123", required = true)
    private String newPassword;
    
    @NotBlank(message = "确认密码不能为空")
    @Schema(description = "确认新密码", example = "newPassword123", required = true)
    private String confirmPassword;
}
