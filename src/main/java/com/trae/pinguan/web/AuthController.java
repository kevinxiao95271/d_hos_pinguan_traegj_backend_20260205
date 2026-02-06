package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.service.JwtService;
import com.trae.pinguan.service.UserService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.LoginRequest;
import com.trae.pinguan.web.dto.LoginResponse;
import io.swagger.v3.oas.annotations.Operation;
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

    @PostMapping("/login")
    @Operation(summary = "登录并返回 JWT")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        UserAccount user = userService.loginOrCreate(request);
        return ApiResponse.ok(new LoginResponse(
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
        ));
    }
}
