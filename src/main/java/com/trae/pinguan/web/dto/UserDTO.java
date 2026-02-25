package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.RoleType;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "用户信息")
public class UserDTO {
    
    @Schema(description = "用户ID")
    private Long id;
    
    @Schema(description = "手机号")
    private String phone;
    
    @Schema(description = "姓名")
    private String name;
    
    @Schema(description = "职称")
    private String title;
    
    @Schema(description = "角色")
    private RoleType role;
    
    @Schema(description = "机构ID")
    private Long institutionId;
    
    @Schema(description = "机构名称")
    private String institutionName;
    
    @Schema(description = "地区")
    private String region;
    
    @Schema(description = "评委组代码")
    private String reviewerGroupCode;
    
    @Schema(description = "面试组代码")
    private String interviewGroupCode;
    
    @Schema(description = "专家背景")
    private String expertBackground;
    
    @Schema(description = "启用状态")
    private Boolean enabled;
    
    @Schema(description = "注册时间")
    private LocalDateTime createdAt;
    
    @Schema(description = "最后登录时间")
    private LocalDateTime lastLoginAt;
    
    public static UserDTO from(UserAccount user) {
        return UserDTO.builder()
                .id(user.getId())
                .phone(user.getPhone())
                .name(user.getName())
                .title(user.getTitle())
                .role(user.getRole())
                .institutionId(user.getInstitution() != null ? user.getInstitution().getId() : null)
                .institutionName(user.getInstitution() != null ? user.getInstitution().getName() : null)
                .region(user.getInstitution() != null ? user.getInstitution().getRegion() : null)
                .reviewerGroupCode(user.getReviewerGroupCode())
                .interviewGroupCode(user.getInterviewGroupCode())
                .expertBackground(user.getExpertBackground())
                .enabled(user.getEnabled())
                .createdAt(user.getCreatedAt())
                .lastLoginAt(user.getLastLoginAt())
                .build();
    }
}
