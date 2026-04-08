package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.ReviewerInstitutionChange;
import com.trae.pinguan.service.ReviewerService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.ChangeInstitutionRequest;
import com.trae.pinguan.web.dto.ReviewerProfileDto;
import com.trae.pinguan.web.dto.ReviewerProfileUpsertRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.io.InputStream;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
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

    @PostMapping("/profile/id-card")
    @Operation(summary = "上传身份证图片（side=FRONT 或 BACK）")
    public ApiResponse<ReviewerProfileDto> uploadIdCard(
            @RequestParam String side,
            @RequestPart MultipartFile file) {
        Long reviewerId = getCurrentReviewerId();
        return ApiResponse.ok(reviewerService.uploadIdCard(reviewerId, side, file));
    }

    @GetMapping("/profile/id-card/{side}")
    @Operation(summary = "查看身份证图片（side=FRONT 或 BACK）")
    public ResponseEntity<InputStreamResource> viewIdCard(@PathVariable String side) {
        Long reviewerId = getCurrentReviewerId();
        InputStream stream = reviewerService.getIdCardStream(reviewerId, side);
        return ResponseEntity.ok()
                .contentType(MediaType.IMAGE_JPEG)
                .body(new InputStreamResource(stream));
    }

    @PutMapping("/institution")
    @Operation(summary = "修改本人所属机构（自助申请，操作记录留存）")
    public ApiResponse<Void> changeMyInstitution(
            @Valid @RequestBody ChangeInstitutionRequest req,
            HttpServletRequest request) {
        Long reviewerId = getCurrentReviewerId();
        String operatorName = (String) request.getAttribute("userName");
        reviewerService.changeInstitution(reviewerId, req, reviewerId, operatorName);
        return ApiResponse.ok(null);
    }

    @GetMapping("/institution/history")
    @Operation(summary = "查看本人所属机构变更记录")
    public ApiResponse<List<ReviewerInstitutionChange>> myInstitutionHistory() {
        Long reviewerId = getCurrentReviewerId();
        return ApiResponse.ok(reviewerService.getInstitutionHistory(reviewerId));
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
