package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Pattern;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
@Schema(description = "管理员创建评委账号请求")
public class CreateReviewerRequest {
    
    @NotBlank(message = "手机号不能为空")
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    @Schema(description = "手机号", example = "13800138000", required = true)
    private String phone;
    
    @NotBlank(message = "姓名不能为空")
    @Size(max = 64, message = "姓名长度不能超过64个字符")
    @Schema(description = "真实姓名", example = "张三", required = true)
    private String name;
    
    @Size(max = 64, message = "职称长度不能超过64个字符")
    @Schema(description = "职称", example = "主任医师")
    private String title;
    
    @NotNull(message = "所属机构不能为空")
    @Schema(description = "所属机构ID", example = "123", required = true)
    private Long institutionId;
    
    @Schema(description = "评委组代码", example = "GROUP_A")
    private String reviewerGroupCode;
    
    @Schema(description = "面试组代码", example = "INTERVIEW_1")
    private String interviewGroupCode;
    
    @Schema(description = "专家背景", example = "心内科")
    private String expertBackground;
}
