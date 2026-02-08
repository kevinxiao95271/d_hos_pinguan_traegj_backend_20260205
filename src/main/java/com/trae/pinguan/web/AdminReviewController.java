package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import com.trae.pinguan.service.ReviewService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.ReviewAutoAssignRequest;
import com.trae.pinguan.web.dto.ReviewFeedbackItem;
import com.trae.pinguan.web.dto.ReviewRankingItem;
import com.trae.pinguan.web.dto.ReviewSummaryItem;
import com.trae.pinguan.web.dto.ReviewTaskAssignRequest;
import com.trae.pinguan.web.dto.ReviewScoreReturnRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin/reviews")
@RequiredArgsConstructor
@Tag(name = "后台评审")
@SecurityRequirement(name = "BearerAuth")
public class AdminReviewController {
    private final ReviewService reviewService;
    private final com.trae.pinguan.service.ReviewerService reviewerService;

    @PostMapping("/tasks")
    @Operation(summary = "后台分配评审任务")
    public ApiResponse<ReviewTask> assign(@Valid @RequestBody ReviewTaskAssignRequest request) {
        return ApiResponse.ok(reviewService.assignTask(request));
    }

    @PostMapping("/auto-assign")
    @Operation(summary = "后台自动分配评审任务")
    public ApiResponse<List<ReviewTask>> autoAssign(@Valid @RequestBody ReviewAutoAssignRequest request) {
        return ApiResponse.ok(reviewService.autoAssign(request));
    }

    @GetMapping("/tasks")
    @Operation(summary = "后台查询已分配任务列表")
    public ApiResponse<List<com.trae.pinguan.web.dto.AdminReviewTaskItem>> listTasks(
            @RequestParam Long competitionId,
            @RequestParam ReviewStage stage,
            @RequestParam(required = false) ReviewStatus status) {
        return ApiResponse.ok(reviewService.listTasksForAdmin(competitionId, stage, status));
    }

    @GetMapping("/summary")
    @Operation(summary = "后台评分汇总")
    public ApiResponse<List<ReviewSummaryItem>> summary(@RequestParam Long competitionId,
                                                        @RequestParam ReviewStage stage) {
        return ApiResponse.ok(reviewService.summaryByStage(competitionId, stage));
    }

    @GetMapping("/rankings")
    @Operation(summary = "后台评分排名")
    public ApiResponse<List<ReviewRankingItem>> rankings(@RequestParam Long competitionId,
                                                         @RequestParam ReviewStage stage,
                                                         @RequestParam(required = false) GroupType groupType) {
        return ApiResponse.ok(reviewService.rankingByStage(competitionId, stage, groupType));
    }

    @GetMapping("/reviewers")
    @Operation(summary = "后台评委列表")
    public ApiResponse<java.util.List<com.trae.pinguan.web.dto.ReviewerListItem>> reviewers(
            @RequestParam(required = false) Long institutionId,
            @RequestParam(required = false) String reviewerGroupCode,
            @RequestParam(required = false) String interviewGroupCode,
            @RequestParam(required = false) String expertBackground) {
        return com.trae.pinguan.web.dto.ApiResponse.ok(
                reviewerService.list(institutionId, reviewerGroupCode, interviewGroupCode, expertBackground));
    }

    @GetMapping("/shortlist")
    @Operation(summary = "后台入围名单")
    public ApiResponse<List<ReviewRankingItem>> shortlist(@RequestParam Long competitionId,
                                                          @RequestParam ReviewStage stage,
                                                          @RequestParam(required = false) GroupType groupType,
                                                          @RequestParam(required = false) Integer limit,
                                                          @RequestParam(required = false) Double minAvgTotal) {
        int size = limit == null ? 10 : Math.max(1, limit);
        List<ReviewRankingItem> rankings = reviewService.rankingByStage(competitionId, stage, groupType);
        return ApiResponse.ok(rankings.stream()
                .filter(item -> minAvgTotal == null || item.getAvgTotal() >= minAvgTotal)
                .limit(size)
                .collect(java.util.stream.Collectors.toList()));
    }

    @GetMapping("/feedback")
    @Operation(summary = "后台专家意见反馈")
    public ApiResponse<List<ReviewFeedbackItem>> feedback(@RequestParam Long competitionId,
                                                          @RequestParam ReviewStage stage) {
        return ApiResponse.ok(reviewService.feedbackByStage(competitionId, stage));
    }

    @PostMapping("/scores/return")
    @Operation(summary = "后台退回评审评分")
    public ApiResponse<ReviewTask> returnScore(@Valid @RequestBody ReviewScoreReturnRequest request) {
        return ApiResponse.ok(reviewService.returnScore(request));
    }
}
