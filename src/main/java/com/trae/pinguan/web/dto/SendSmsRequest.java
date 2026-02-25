package com.trae.pinguan.web.dto;

import com.trae.pinguan.service.SmsService.SmsCodeType;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Pattern;
import lombok.Data;

@Data
@Schema(description = "发送短信验证码请求")
public class SendSmsRequest {
    
    @NotBlank(message = "手机号不能为空")
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    @Schema(description = "手机号", example = "13800138000", required = true)
    private String phone;
    
    @NotNull(message = "验证码类型不能为空")
    @Schema(description = "验证码类型", example = "REGISTER", required = true,
            allowableValues = {"REGISTER", "LOGIN", "RESET_PASSWORD", "CHANGE_PHONE"})
    private SmsCodeType type;
}
