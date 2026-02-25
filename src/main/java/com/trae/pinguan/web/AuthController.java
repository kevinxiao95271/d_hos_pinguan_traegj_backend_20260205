package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.service.JwtService;
import com.trae.pinguan.service.SmsService;
import com.trae.pinguan.service.UserService;
import com.trae.pinguan.web.dto.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Tag(name = "认证")
public class AuthController {
    private final UserService userService;
    private final JwtService jwtService;
    private final SmsService smsService;

    @PostMapping("/register")
    @Operation(
        summary = "参赛者注册", 
        description = "仅限参赛者（CONTESTANT）自助注册。评委由管理员创建账号，无需注册。"
    )
    public ApiResponse<LoginResponse> register(@Valid @RequestBody RegisterRequest request) {
        try {
            // 仅允许参赛者注册
            if (request.getRole() != com.trae.pinguan.domain.enums.RoleType.CONTESTANT) {
                return ApiResponse.fail("仅允许参赛者自助注册，评委请联系管理员创建账号");
            }
            
            UserAccount user = userService.register(request);
            return ApiResponse.ok(buildLoginResponse(user));
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }
    
    @PostMapping("/login-with-password")
    @Operation(summary = "密码登录", description = "使用手机号和密码登录")
    public ApiResponse<LoginResponse> loginWithPassword(@Valid @RequestBody LoginWithPasswordRequest request) {
        try {
            UserAccount user = userService.login(request);
            return ApiResponse.ok(buildLoginResponse(user));
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }
    
    @PostMapping("/change-password/{userId}")
    @SecurityRequirement(name = "BearerAuth")
    @Operation(summary = "修改密码", description = "用户修改自己的密码")
    public ApiResponse<String> changePassword(
            @Parameter(description = "用户ID", required = true) @PathVariable Long userId,
            @Valid @RequestBody ChangePasswordRequest request) {
        try {
            userService.changePassword(userId, request);
            return ApiResponse.ok("密码修改成功");
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }

    @PostMapping("/login")
    @Operation(
        summary = "登录并返回 JWT（兼容旧版）", 
        description = "⚠️ 不推荐使用：无密码验证，仅用于向后兼容。推荐使用 /login-with-password"
    )
    @Deprecated
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        UserAccount user = userService.loginOrCreate(request);
        return ApiResponse.ok(buildLoginResponse(user));
    }
    
    private LoginResponse buildLoginResponse(UserAccount user) {
        return new LoginResponse(
                user.getId(),
                user.getPhone(),
                user.getName(),
                user.getTitle(),
                user.getRole(),
                user.getInstitution() == null ? null : user.getInstitution().getId(),
                user.getInstitution() == null ? null : user.getInstitution().getName(),
                user.getInstitution() == null ? null : user.getInstitution().getCode(),
                user.getInstitution() == null ? null : user.getInstitution().getUscc(),
                user.getExpertBackground(),
                jwtService.generateToken(user)
        );
    }
}
