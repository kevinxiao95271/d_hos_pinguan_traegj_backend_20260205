package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.ReviewScore;
import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import com.trae.pinguan.service.ReviewService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.ReviewAutoAssignRequest;
import com.trae.pinguan.web.dto.ReviewRankingItem;
import com.trae.pinguan.web.dto.ReviewScoreRequest;
import com.trae.pinguan.web.dto.ReviewSummaryItem;
import com.trae.pinguan.web.dto.ReviewTaskAssignRequest;
import com.trae.pinguan.web.dto.ReviewTaskItem;
import com.trae.pinguan.web.dto.ReviewTaskStatusRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/reviews")
@RequiredArgsConstructor
@Tag(name = "评审")
@SecurityRequirement(name = "BearerAuth")
public class ReviewController {
    private final ReviewService reviewService;
    private final javax.servlet.http.HttpServletRequest request;

    @PostMapping("/tasks")
    @Operation(summary = "分配评审任务")
    public ApiResponse<ReviewTask> assign(@Valid @RequestBody ReviewTaskAssignRequest request) {
        return ApiResponse.ok(reviewService.assignTask(request));
    }

    @PostMapping("/auto-assign")
    @Operation(summary = "自动分配评审任务")
    public ApiResponse<List<ReviewTask>> autoAssign(@Valid @RequestBody ReviewAutoAssignRequest request) {
        return ApiResponse.ok(reviewService.autoAssign(request));
    }

    @PutMapping("/tasks/status")
    @Operation(summary = "更新评审任务状态")
    public ApiResponse<ReviewTask> updateStatus(@Valid @RequestBody ReviewTaskStatusRequest request) {
        return ApiResponse.ok(reviewService.updateStatus(request));
    }

    @GetMapping("/my-tasks")
    @Operation(summary = "我的评审任务（评委端）")
    @org.springframework.transaction.annotation.Transactional(readOnly = true)
    public ApiResponse<List<ReviewTaskItem>> myTasks() {
        // 从token中获取当前登录用户ID
        Long reviewerId = getCurrentUserId();
        List<ReviewTask> tasks = reviewService.listTasks(reviewerId);
        // 转换为DTO，包含registrationId和projectName
        List<ReviewTaskItem> items = tasks.stream()
                .map(task -> {
                    // 在事务中访问懒加载的registration和institution
                    Registration reg = task.getRegistration();
                    return ReviewTaskItem.builder()
                            .id(task.getId())
                            .registrationId(reg != null ? reg.getId() : null)
                            .projectName(reg != null ? reg.getProjectName() : null)
                            .institutionName(reg != null && reg.getInstitution() != null 
                                    ? reg.getInstitution().getName() : null)
                            .institutionLevel(reg != null && reg.getInstitution() != null 
                                    ? reg.getInstitution().getLevel() : null)
                            .stage(task.getStage())
                            .status(task.getStatus())
                            .createdAt(task.getCreatedAt())
                            .build();
                })
                .collect(java.util.stream.Collectors.toList());
        return ApiResponse.ok(items);
    }

    @GetMapping("/tasks")
    @Operation(summary = "评审任务列表（需要reviewerId参数）")
    public ApiResponse<List<ReviewTask>> list(@RequestParam Long reviewerId) {
        return ApiResponse.ok(reviewService.listTasks(reviewerId));
    }
    
    private Long getCurrentUserId() {
        Object userId = request.getAttribute("userId");
        if (userId == null) {
            throw new RuntimeException("未登录");
        }
        return Long.parseLong(userId.toString());
    }

    @GetMapping("/tasks/filter")
    @Operation(summary = "评审任务筛选")
    public ApiResponse<List<ReviewTask>> listWithFilter(@RequestParam Long reviewerId,
                                                        @RequestParam(required = false) ReviewStage stage,
                                                        @RequestParam(required = false) ReviewStatus status) {
        return ApiResponse.ok(reviewService.listTasks(reviewerId, stage, status));
    }

    @GetMapping("/tasks/stage")
    @Operation(summary = "按阶段查询评审任务")
    public ApiResponse<List<ReviewTask>> listByStage(@RequestParam Long competitionId,
                                                     @RequestParam ReviewStage stage,
                                                     @RequestParam(required = false) ReviewStatus status) {
        return ApiResponse.ok(reviewService.listTasksByStage(competitionId, stage, status));
    }

    @PostMapping("/scores")
    @Operation(summary = "提交评分")
    public ApiResponse<ReviewScore> submitScore(@Valid @RequestBody ReviewScoreRequest request) {
        return ApiResponse.ok(reviewService.submitScore(request));
    }

    @GetMapping("/scores/{reviewTaskId}")
    @Operation(summary = "查询评分详情")
    public ApiResponse<ReviewScore> getScore(@PathVariable Long reviewTaskId) {
        return reviewService.getScore(reviewTaskId)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("评分不存在"));
    }

    @GetMapping("/summary")
    @Operation(summary = "阶段评分汇总")
    public ApiResponse<List<ReviewSummaryItem>> summary(@RequestParam Long competitionId,
                                                        @RequestParam ReviewStage stage) {
        return ApiResponse.ok(reviewService.summaryByStage(competitionId, stage));
    }

    @GetMapping("/rankings")
    @Operation(summary = "阶段评分排名")
    public ApiResponse<List<ReviewRankingItem>> rankings(@RequestParam Long competitionId,
                                                         @RequestParam ReviewStage stage,
                                                         @RequestParam(required = false) GroupType groupType) {
        return ApiResponse.ok(reviewService.rankingByStage(competitionId, stage, groupType));
    }
}
