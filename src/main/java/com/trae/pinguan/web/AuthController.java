package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.service.CompetitionService;
import com.trae.pinguan.service.JwtService;
import com.trae.pinguan.service.SmsService;
import com.trae.pinguan.service.UserService;
import com.trae.pinguan.web.dto.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.Arrays;
import java.util.List;
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

    /**
     * 当前系统启用的须知 key，与前端 src/config/integrityNotices.js 顺序对齐。
     * 新增须知时在此处追加，无需改数据库结构。
     */
    private static final List<String> ACTIVE_NOTICE_KEYS = Arrays.asList("BOOK", "INTERVIEW", "FINAL");

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
        // 优先使用 OPS 设定的全局当前赛事；未设定时回退 ID 最大赛事
        Optional<Competition> latestCompetition = competitionService.getCurrent();

        // pendingIntegrityNoticeKeys 仅对评审专家计算；其他角色无须弹窗，返回 null
        List<String> pendingKeys = null;
        if (RoleType.REVIEWER.equals(user.getRole())) {
            pendingKeys = userService.getPendingNoticeKeys(user.getId(), ACTIVE_NOTICE_KEYS);
        }

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
                user.getNoticeConfirmedAt() != null,  // 兼容旧前端
                pendingKeys
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
    @Operation(
        summary = "确认已阅读诚信须知",
        description = "登录后首次弹窗强制阅读须知，阅读完毕后调用此接口。" +
                      "请求体带 noticeKey（BOOK / INTERVIEW）；仅评审专家（REVIEWER）可调用。" +
                      "旧版无 body 调用兼容策略：视为确认 BOOK。"
    )
    public ApiResponse<Void> confirmNotice(
            @org.springframework.web.bind.annotation.RequestBody(required = false)
            @javax.validation.Valid NoticeConfirmRequest body,
            HttpServletRequest request) {

        Object userIdAttr = request.getAttribute("userId");
        if (userIdAttr == null) {
            return ApiResponse.fail("未登录");
        }
        String role = (String) request.getAttribute("role");
        if (!"REVIEWER".equals(role)) {
            return ApiResponse.fail("仅评审专家可调用此接口");
        }

        Long userId = Long.parseLong(userIdAttr.toString());
        // 旧版无 body 兼容：默认确认 BOOK
        String noticeKey = (body != null && body.getNoticeKey() != null) ? body.getNoticeKey() : "BOOK";
        userService.confirmNotice(userId, noticeKey);
        return ApiResponse.ok(null);
    }
}
