package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.service.CompetitionService;
import com.trae.pinguan.service.JwtService;
import com.trae.pinguan.service.SmsService;
import com.trae.pinguan.service.UserService;
import com.trae.pinguan.web.dto.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.Optional;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Tag(name = "认证")
public class AuthController {
    private final UserService userService;
    private final JwtService jwtService;
    private final SmsService smsService;
    private final CompetitionService competitionService;

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
        // 获取最新赛事作为默认选中
        Optional<Competition> latestCompetition = competitionService.getLatest();
        
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
                jwtService.generateToken(user),
                latestCompetition.map(Competition::getId).orElse(null),
                latestCompetition.map(Competition::getName).orElse(null),
                user.getNoticeConfirmedAt() != null
        );
    }

    @PostMapping("/self-change-password")
    @SecurityRequirement(name = "BearerAuth")
    @Operation(summary = "本人修改密码", description = "登录用户修改自己的密码，需提供旧密码验证身份")
    public ApiResponse<String> selfChangePassword(
            @Valid @RequestBody ChangePasswordRequest request,
            HttpServletRequest httpRequest) {
        Object userIdAttr = httpRequest.getAttribute("userId");
        if (userIdAttr == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "未登录");
        }
        Long userId = Long.parseLong(userIdAttr.toString());
        try {
            userService.changePassword(userId, request);
            return ApiResponse.ok("密码修改成功");
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }

    @PostMapping("/notice/confirm")
    @SecurityRequirement(name = "BearerAuth")
    @Operation(summary = "确认已阅读诚信须知", description = "登录后首次弹窗强制阅读须知，阅读完毕后调用此接口记录确认时间")
    public ApiResponse<Void> confirmNotice(javax.servlet.http.HttpServletRequest request) {
        Object userId = request.getAttribute("userId");
        if (userId == null) {
            return ApiResponse.fail("未登录");
        }
        userService.confirmNotice(Long.parseLong(userId.toString()));
        return ApiResponse.ok(null);
    }
}
