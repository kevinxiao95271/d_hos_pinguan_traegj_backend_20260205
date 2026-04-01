package com.trae.pinguan.web;

import com.trae.pinguan.service.ReviewerService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.ReviewerProfileDto;
import com.trae.pinguan.web.dto.ReviewerProfileUpsertRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/reviewers/me")
@RequiredArgsConstructor
@Tag(name = "评委档案")
@SecurityRequirement(name = "BearerAuth")
public class ReviewerProfileController {
    private final ReviewerService reviewerService;
    private final javax.servlet.http.HttpServletRequest request;

    @GetMapping("/profile")
    @Operation(summary = "我的扩展档案")
    public ApiResponse<ReviewerProfileDto> myProfile() {
        Long reviewerId = getCurrentReviewerId();
        return ApiResponse.ok(reviewerService.getProfile(reviewerId));
    }

    @PutMapping("/profile")
    @Operation(summary = "更新我的扩展档案")
    public ApiResponse<ReviewerProfileDto> upsertMyProfile(
            @Valid @RequestBody ReviewerProfileUpsertRequest req) {
        Long reviewerId = getCurrentReviewerId();
        return ApiResponse.ok(reviewerService.upsertProfile(reviewerId, req));
    }

    private Long getCurrentReviewerId() {
        Object userId = request.getAttribute("userId");
        if (userId == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "未登录");
        }
        String role = String.valueOf(request.getAttribute("role"));
        if (!"REVIEWER".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "仅评委可修改本人档案");
        }
        return Long.parseLong(userId.toString());
    }
}
