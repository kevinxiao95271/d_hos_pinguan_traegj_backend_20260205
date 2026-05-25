package com.trae.pinguan.web;

import com.trae.pinguan.service.FinalService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.FinalScoreRequest;
import com.trae.pinguan.web.dto.FinalTaskItem;
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
    private final HttpServletRequest request;

    // ── 我的现场任务 ──────────────────────────────────────────────────────────

    @GetMapping("/my-tasks")
    @Operation(summary = "获取本人现场评分任务列表",
               description = "按专场+顺序排序，含已保存草稿评分")
    public ApiResponse<List<FinalTaskItem>> myTasks() {
        return ApiResponse.ok(finalService.myFinalTasks(getCurrentUserId()));
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

    private Long getCurrentUserId() {
        Object userId = request.getAttribute("userId");
        if (userId == null) throw new RuntimeException("未登录");
        return Long.parseLong(userId.toString());
    }
}
