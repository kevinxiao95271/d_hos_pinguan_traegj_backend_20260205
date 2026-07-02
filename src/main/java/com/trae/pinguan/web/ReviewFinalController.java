package com.trae.pinguan.web;

import com.trae.pinguan.service.FinalService;
import com.trae.pinguan.service.ReviewService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.FinalScoreRequest;
import com.trae.pinguan.web.dto.FinalTaskItem;
import com.trae.pinguan.web.dto.RecuseRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/reviews/final")
@RequiredArgsConstructor
@Tag(name = "评委-现场评分")
@SecurityRequirement(name = "BearerAuth")
public class ReviewFinalController {

    private final FinalService finalService;
    private final ReviewService reviewService;
    private final HttpServletRequest request;

    // ── 我的现场任务 ──────────────────────────────────────────────────────────

    @GetMapping("/my-tasks")
    @Operation(summary = "获取本人现场评分任务列表",
               description = "按专场+顺序排序，含已保存草稿评分。competitionId 不传返回全部届次")
    public ApiResponse<List<FinalTaskItem>> myTasks(
            @RequestParam(required = false) Long competitionId) {
        return ApiResponse.ok(finalService.myFinalTasks(getCurrentUserId(), competitionId));
    }

    // ── 保存草稿 ──────────────────────────────────────────────────────────────

    @PutMapping("/scores/{taskId}/draft")
    @Operation(summary = "保存评分草稿", description = "暂存评分，任务状态变为 IN_PROGRESS")
    public ApiResponse<Void> saveDraft(
            @PathVariable Long taskId,
            @Valid @RequestBody FinalScoreRequest req) {
        finalService.saveScore(taskId, getCurrentUserId(), req, false);
        return ApiResponse.ok(null);
    }

    // ── 正式提交 ──────────────────────────────────────────────────────────────

    @PutMapping("/scores/{taskId}/submit")
    @Operation(summary = "提交最终评分", description = "提交后任务状态变为 SUBMITTED，不可再次提交")
    public ApiResponse<Void> submitScore(
            @PathVariable Long taskId,
            @Valid @RequestBody FinalScoreRequest req) {
        finalService.saveScore(taskId, getCurrentUserId(), req, true);
        return ApiResponse.ok(null);
    }

    // ── 规避 ─────────────────────────────────────────────────────────────────

    @PutMapping("/scores/{taskId}/recuse")
    @Operation(summary = "申请规避（决赛轮）",
               description = "任务状态变为 RECUSED，stage=FINAL 可与其他轮次规避数据区分。" +
                             "reasonCode 取值见 GET /api/dictionaries?type=recuse_reason")
    public ApiResponse<Void> recuse(
            @PathVariable Long taskId,
            @Valid @RequestBody RecuseRequest req) {
        reviewService.recuseTask(taskId, req, getCurrentUserId());
        return ApiResponse.ok(null);
    }

    @DeleteMapping("/scores/{taskId}/recuse")
    @Operation(summary = "撤销规避（决赛轮）",
               description = "将 RECUSED 任务恢复为 PENDING 或 DRAFT，仅规避后未提交时可撤销")
    public ApiResponse<Void> undoRecuse(@PathVariable Long taskId) {
        reviewService.undoRecuseTask(taskId, getCurrentUserId());
        return ApiResponse.ok(null);
    }

    private Long getCurrentUserId() {
        Object userId = request.getAttribute("userId");
        if (userId == null) throw new RuntimeException("未登录");
        return Long.parseLong(userId.toString());
    }
}
