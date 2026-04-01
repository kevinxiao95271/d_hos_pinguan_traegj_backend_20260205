package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.service.JwtService;
import com.trae.pinguan.service.ReviewerService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.ReviewerListItem;
import com.trae.pinguan.web.dto.ReviewerProfileDto;
import com.trae.pinguan.web.dto.ReviewerProfileUpsertRequest;
import com.trae.pinguan.web.dto.ReviewerUpsertRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/admin/reviewers")
@RequiredArgsConstructor
@Tag(name = "后台评委管理")
@SecurityRequirement(name = "BearerAuth")
public class AdminReviewerController {
    private final ReviewerService reviewerService;
    private final JwtService jwtService;
    private final HttpServletRequest request;

    @GetMapping
    @Operation(summary = "评委列表")
    public ApiResponse<List<ReviewerListItem>> list(@RequestParam(required = false) Long competitionId,
                                                    @RequestParam(required = false) Long institutionId,
                                                    @RequestParam(required = false) String reviewerGroupCode,
                                                    @RequestParam(required = false) String interviewGroupCode,
                                                    @RequestParam(required = false) String expertBackground) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.list(institutionId, reviewerGroupCode, interviewGroupCode, expertBackground));
    }

    @GetMapping("/list")
    @Operation(summary = "评委列表(兼容路径)")
    public ApiResponse<List<ReviewerListItem>> listCompat(@RequestParam(required = false) Long competitionId,
                                                          @RequestParam(required = false) Long institutionId,
                                                          @RequestParam(required = false) String reviewerGroupCode,
                                                          @RequestParam(required = false) String interviewGroupCode,
                                                          @RequestParam(required = false) String expertBackground) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.list(institutionId, reviewerGroupCode, interviewGroupCode, expertBackground));
    }

    @GetMapping("/{id}")
    @Operation(summary = "评委详情")
    public ApiResponse<UserAccount> detail(@PathVariable Long id) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.get(id));
    }

    @PostMapping
    @Operation(summary = "新增评委")
    public ApiResponse<UserAccount> create(@Valid @RequestBody ReviewerUpsertRequest request) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.create(request));
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新评委")
    public ApiResponse<UserAccount> update(@PathVariable Long id,
                                           @Valid @RequestBody ReviewerUpsertRequest request) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.update(id, request));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除评委")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        requireCommitteeOrOps();
        reviewerService.delete(id);
        return ApiResponse.ok(null);
    }

    @GetMapping("/{id}/profile")
    @Operation(summary = "评审专家扩展档案详情")
    public ApiResponse<ReviewerProfileDto> profile(@PathVariable Long id) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.getProfile(id));
    }

    @PutMapping("/{id}/profile")
    @Operation(summary = "更新评审专家扩展档案")
    public ApiResponse<ReviewerProfileDto> upsertProfile(@PathVariable Long id,
                                                         @Valid @RequestBody ReviewerProfileUpsertRequest request) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.upsertProfile(id, request));
    }

    private void requireCommitteeOrOps() {
        // 从request attributes中获取Filter已验证的角色信息
        String role = (String) request.getAttribute("role");
        if (role == null || role.trim().isEmpty()) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "未登录");
        }
        // 允许COMMITTEE、COMMITTEE_ADMIN和OPS角色访问
        if (!"COMMITTEE".equals(role) && !"COMMITTEE_ADMIN".equals(role) && !"OPS".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "无权限");
        }
    }

    // extractToken方法已不需要，改为直接从request attributes获取Filter验证后的信息
}
