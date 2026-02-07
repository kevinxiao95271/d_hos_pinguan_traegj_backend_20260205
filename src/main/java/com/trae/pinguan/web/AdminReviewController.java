package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
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

    @GetMapping("/summary")
    @Operation(summary = "后台评分汇总")
    public ApiResponse<List<ReviewSummaryItem>> summary(@RequestParam Long competitionId,
                                                        @RequestParam ReviewStage stage) {
        return ApiResponse.ok(reviewService.summaryByStage(competitionId, stage));
    }

    @GetMapping("/rankings")
    @Operation(summary = "后台评分排名（支持分页）",
               description = "获取指定赛事和阶段的评分排名，支持分组筛选和分页：\n" +
                             "【分页参数】\n" +
                             "- page: 页码（从1开始），不传则返回全部数据\n" +
                             "- size: 每页数量，默认20\n\n" +
                             "【返回格式】\n" +
                             "- 不分页: 返回数组 []\n" +
                             "- 分页: 返回对象 {content: [], pageNo: 1, pageSize: 20, totalCount: 100, ...}")
    public ApiResponse<?> rankings(@RequestParam Long competitionId,
                                   @RequestParam ReviewStage stage,
                                   @RequestParam(required = false) GroupType groupType,
                                   @RequestParam(required = false) Integer page,
                                   @RequestParam(required = false) Integer size) {
        return ApiResponse.ok(reviewService.rankingByStage(competitionId, stage, groupType, page, size));
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
    @Operation(summary = "后台入围名单（支持分页）",
               description = "获取入围名单，支持分数线筛选和分页：\n" +
                             "【筛选参数】\n" +
                             "- minAvgTotal: 最低分数线（可选）\n" +
                             "- limit: 前N名（可选，与page互斥）\n\n" +
                             "【分页参数】\n" +
                             "- page: 页码（从1开始），不传则使用limit模式\n" +
                             "- size: 每页数量，默认20\n\n" +
                             "【返回格式】\n" +
                             "- limit模式: 返回数组 []（前N名）\n" +
                             "- 分页模式: 返回对象 {content: [], pageNo: 1, pageSize: 20, totalCount: 100, ...}")
    public ApiResponse<?> shortlist(@RequestParam Long competitionId,
                                    @RequestParam ReviewStage stage,
                                    @RequestParam(required = false) GroupType groupType,
                                    @RequestParam(required = false) Integer limit,
                                    @RequestParam(required = false) Double minAvgTotal,
                                    @RequestParam(required = false) Integer page,
                                    @RequestParam(required = false) Integer size) {
        
        // 如果有page参数，使用分页模式
        if (page != null) {
            return ApiResponse.ok(reviewService.shortlistWithPagination(
                    competitionId, stage, groupType, minAvgTotal, page, size));
        }
        
        // 否则使用limit模式（兼容旧版）
        int limitSize = limit == null ? 10 : Math.max(1, limit);
        
        // 获取排名列表（不分页）
        Object rankingsObj = reviewService.rankingByStage(competitionId, stage, groupType, null, null);
        List<ReviewRankingItem> rankings;
        
        if (rankingsObj instanceof List) {
            @SuppressWarnings("unchecked")
            List<ReviewRankingItem> temp = (List<ReviewRankingItem>) rankingsObj;
            rankings = temp;
        } else {
            // 如果返回的是其他类型，返回空列表
            rankings = new java.util.ArrayList<>();
        }
        
        return ApiResponse.ok(rankings.stream()
                .filter(item -> minAvgTotal == null || item.getAvgTotal() >= minAvgTotal)
                .limit(limitSize)
                .collect(java.util.stream.Collectors.toList()));
    }

    @Deprecated
    @GetMapping("/feedback")
    @Operation(summary = "后台专家意见反馈", deprecated = true, 
               description = "⚠️ 已废弃：请使用 GET /api/registrations/{id}/reviewer-scores 代替。新API提供更完整的评委评分详情（包含分项评分、评委单位、职称等）")
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
