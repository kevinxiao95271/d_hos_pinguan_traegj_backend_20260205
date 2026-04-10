package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.InterviewScore;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.ReviewScore;
import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import com.trae.pinguan.service.ReviewService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.InterviewScoreRequest;
import com.trae.pinguan.web.dto.ReviewAutoAssignRequest;
import com.trae.pinguan.web.dto.ReviewRankingItem;
import com.trae.pinguan.web.dto.ReviewScoreRequest;
import com.trae.pinguan.web.dto.ReviewSummaryItem;
import com.trae.pinguan.web.dto.ReviewTaskAssignRequest;
import com.trae.pinguan.web.dto.ReviewTaskItem;
import com.trae.pinguan.web.dto.RecuseRequest;
import com.trae.pinguan.web.dto.ReviewScoreDraftRequest;
import com.trae.pinguan.web.dto.InterviewScoreDraftRequest;
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
    public ApiResponse<List<ReviewTaskItem>> myTasks() {
        Long reviewerId = getCurrentUserId();
        return ApiResponse.ok(reviewService.myTaskItems(reviewerId));
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

    @PostMapping("/interview-scores")
    @Operation(summary = "提交面谈评分（评委端）")
    public ApiResponse<InterviewScore> submitInterviewScore(
            @Valid @RequestBody InterviewScoreRequest req) {
        return ApiResponse.ok(reviewService.submitInterviewScore(req));
    }

    @GetMapping("/interview-scores/{reviewTaskId}")
    @Operation(summary = "查询面谈评分详情")
    public ApiResponse<InterviewScore> getInterviewScore(@PathVariable Long reviewTaskId) {
        return reviewService.getInterviewScore(reviewTaskId)
                .map(ApiResponse::ok)
                .orElseGet(() -> ApiResponse.fail("面谈评分不存在"));
    }

    // ─── 规避 ───────────────────────────────────────────────────────────────

    @PostMapping("/tasks/{taskId}/recuse")
    @Operation(summary = "申请规避评审任务", description = "规避原因code来自 GET /api/dictionaries/recuse_reason")
    public ApiResponse<ReviewTask> recuse(@PathVariable Long taskId,
                                          @Valid @RequestBody RecuseRequest req) {
        Long reviewerId = getCurrentUserId();
        return ApiResponse.ok(reviewService.recuseTask(taskId, req, reviewerId));
    }

    @DeleteMapping("/tasks/{taskId}/recuse")
    @Operation(summary = "撤销规避（仅评委本人）",
               description = "将 RECUSED 任务回退：存在草稿分数则回到 DRAFT，否则回到 PENDING。同时清除规避原因。")
    public ApiResponse<ReviewTask> undoRecuse(@PathVariable Long taskId) {
        Long reviewerId = getCurrentUserId();
        return ApiResponse.ok(reviewService.undoRecuseTask(taskId, reviewerId));
    }

    // ─── 草稿保存 ────────────────────────────────────────────────────────────

    @PutMapping("/scores/draft")
    @Operation(summary = "书审评分草稿保存（不改变提交状态，可反复调用）")
    public ApiResponse<ReviewScore> saveBookDraft(@Valid @RequestBody ReviewScoreDraftRequest req) {
        return ApiResponse.ok(reviewService.saveScoreDraft(req));
    }

    @PutMapping("/interview-scores/draft")
    @Operation(summary = "面谈评分草稿保存（不改变提交状态，可反复调用）")
    public ApiResponse<InterviewScore> saveInterviewDraft(@Valid @RequestBody InterviewScoreDraftRequest req) {
        return ApiResponse.ok(reviewService.saveInterviewScoreDraft(req));
    }

    // ─── 统计 ────────────────────────────────────────────────────────────────

    @GetMapping("/my-tasks/stats")
    @Operation(summary = "我的评审任务统计（总数、待提交数、已提交数）")
    public ApiResponse<java.util.Map<String, Long>> myTaskStats() {
        Long reviewerId = getCurrentUserId();
        return ApiResponse.ok(reviewService.myTaskStats(reviewerId));
    }
}
