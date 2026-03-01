package com.trae.pinguan.web;

import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.service.UserService;
import com.trae.pinguan.web.dto.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/admin/users")
@RequiredArgsConstructor
@Tag(name = "用户管理（管理员）")
@SecurityRequirement(name = "BearerAuth")
public class UserManagementController {
    
    private final UserService userService;

    @PostMapping("/{userId}/reset-password")
    @Operation(summary = "重置用户密码（仅OPS）", description = "直接重置为新的6位随机密码，无需旧密码")
    public ApiResponse<Map<String, String>> resetPassword(
            @Parameter(description = "用户ID", required = true) @PathVariable Long userId,
            HttpServletRequest request) {
        String role = (String) request.getAttribute("role");
        if (!RoleType.OPS.name().equals(role)) {
            return ApiResponse.fail("仅系统运维可操作");
        }
        try {
            String newPassword = userService.resetPassword(userId);
            Map<String, String> result = new HashMap<>();
            result.put("newPassword", newPassword);
            return ApiResponse.ok(result);
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }

    @PostMapping("/{userId}/reset-phone")
    @Operation(summary = "重置用户手机号（仅OPS）", description = "将用户的登录手机号更新为新号码")
    public ApiResponse<String> resetPhone(
            @Parameter(description = "用户ID", required = true) @PathVariable Long userId,
            @Parameter(description = "新手机号", required = true) @RequestParam String newPhone,
            HttpServletRequest request) {
        String role = (String) request.getAttribute("role");
        if (!RoleType.OPS.name().equals(role)) {
            return ApiResponse.fail("仅系统运维可操作");
        }
        try {
            userService.resetPhone(userId, newPhone);
            return ApiResponse.ok("手机号已更新");
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }
    
    @PostMapping("/query")
    @Operation(summary = "查询用户列表", description = "支持多条件筛选、分页查询")
    public ApiResponse<Page<UserDTO>> queryUsers(@RequestBody UserQueryRequest request) {
        try {
            Page<UserDTO> users = userService.queryUsers(request);
            return ApiResponse.ok(users);
        } catch (Exception e) {
            return ApiResponse.fail(e.getMessage());
        }
    }
    
    @GetMapping("/{userId}")
    @Operation(summary = "获取用户详情")
    public ApiResponse<UserDTO> getUserDetail(
            @Parameter(description = "用户ID", required = true) @PathVariable Long userId) {
        try {
            UserDTO user = userService.getUserDetail(userId);
            return ApiResponse.ok(user);
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }
    
    @PostMapping("/reviewers")
    @Operation(summary = "创建评委账号", description = "管理员为评委创建账号并分配初始密码")
    public ApiResponse<CreateReviewerResponse> createReviewer(@Valid @RequestBody CreateReviewerRequest request) {
        try {
            CreateReviewerResponse response = userService.createReviewer(request);
            return ApiResponse.ok(response);
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }
    
    @PutMapping("/{userId}/disable")
    @Operation(summary = "禁用用户", description = "禁用后用户无法登录")
    public ApiResponse<String> disableUser(
            @Parameter(description = "用户ID", required = true) @PathVariable Long userId) {
        try {
            userService.disableUser(userId);
            return ApiResponse.ok("用户已禁用");
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }
    
    @PutMapping("/{userId}/enable")
    @Operation(summary = "启用用户", description = "解除禁用状态")
    public ApiResponse<String> enableUser(
            @Parameter(description = "用户ID", required = true) @PathVariable Long userId) {
        try {
            userService.enableUser(userId);
            return ApiResponse.ok("用户已启用");
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }
    
    @GetMapping("/statistics")
    @Operation(summary = "用户统计", description = "统计各类用户数量")
    public ApiResponse<Map<String, Object>> getUserStatistics() {
        Map<String, Object> stats = new HashMap<>();
        
        // 总用户数
        stats.put("totalUsers", userService.countUsers(null, null));
        
        // 启用的用户数
        stats.put("enabledUsers", userService.countUsers(null, true));
        
        // 禁用的用户数
        stats.put("disabledUsers", userService.countUsers(null, false));
        
        // 参赛者数量
        stats.put("contestants", userService.countUsers(RoleType.CONTESTANT, null));
        stats.put("contestantsEnabled", userService.countUsers(RoleType.CONTESTANT, true));
        
        // 评委数量
        stats.put("reviewers", userService.countUsers(RoleType.REVIEWER, null));
        stats.put("reviewersEnabled", userService.countUsers(RoleType.REVIEWER, true));
        
        // 管理员数量
        stats.put("committeeAdmins", userService.countUsers(RoleType.COMMITTEE_ADMIN, null));
        stats.put("opsAdmins", userService.countUsers(RoleType.OPS, null));
        
        return ApiResponse.ok(stats);
    }
}
