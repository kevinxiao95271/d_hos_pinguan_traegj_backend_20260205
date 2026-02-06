package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.RoleType;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class LoginRequest {
    @NotBlank
    private String phone;
    @NotBlank
    private String name;
    private String title;
    @NotNull
    private RoleType role;
    private Long institutionId;
    private String reviewerGroupCode;
    private String interviewGroupCode;
    private String expertBackground;
}
