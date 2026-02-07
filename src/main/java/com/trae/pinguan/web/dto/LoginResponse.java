package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.RoleType;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class LoginResponse {
    private Long id;
    private String phone;
    private String name;
    private String title;
    private RoleType role;
    private Long institutionId;
    private String institutionName;
    private String institutionCode;
    private String institutionUscc;
    private String institutionRegion;
    private String institutionLevel;
    private String expertBackground;
    private String token;
}
