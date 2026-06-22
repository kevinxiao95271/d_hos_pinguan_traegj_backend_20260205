package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.entity.StaffSessionAssignment;
import com.trae.pinguan.domain.enums.ReviewStatus;
import com.trae.pinguan.repository.ReviewScoreRepository;
import com.trae.pinguan.repository.ReviewTaskRepository;
import com.trae.pinguan.repository.StaffSessionAssignmentRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.service.FinalService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.FinalProjectItem;
import com.trae.pinguan.web.dto.FinalRankingItem;
import com.trae.pinguan.web.dto.FinalScheduleSession;
import com.trae.pinguan.web.dto.FinalSessionItem;
import com.trae.pinguan.web.dto.FinalTaskItem;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.stream.Collectors;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/admin/final")
@RequiredArgsConstructor
@Tag(name = "后台-现场竞赛")
@SecurityRequirement(name = "BearerAuth")
public class AdminFinalController {

    private final FinalService finalService;
    private final StaffSessionAssignmentRepository staffSessionRepo;
    private final ReviewTaskRepository reviewTaskRepository;
    private final ReviewScoreRepository reviewScoreRepository;
    private final UserAccountRepository userAccountRepository;
    private final HttpServletRequest request;

    // ── 导入专场分组 ──────────────────────────────────────────────────────────

    @PostMapping("/import-sessions")
    @Operation(summary = "导入专场分组", description = "上传分组 xlsx，解析后写入 registrations 的专场字段")
    public ApiResponse<String> importSessions(
            @RequestParam Long competitionId,
            @Parameter(description = "分组 xlsx 文件") @RequestParam MultipartFile file) throws Exception {
        requireAdminRole();
        String msg = finalService.importSessions(competitionId, file);
        return ApiResponse.ok(msg);
    }

    // ── 专场列表 ──────────────────────────────────────────────────────────────

    @GetMapping("/sessions")
    @Operation(summary = "获取专场列表", description = "返回所有已导入专场及各类型项目数量统计")
    public ApiResponse<List<FinalSessionItem>> listSessions(@RequestParam Long competitionId) {
        return ApiResponse.ok(finalService.listSessions(competitionId));
    }

    // ── 全局场次对应表 ────────────────────────────────────────────────────────

    @GetMapping("/session-schedule")
    @Operation(summary = "全局场次对应表",
               description = "一次返回所有场次（三天×21场）及其项目列表，按日期+场次排序。" +
                             "前端可按 sessionDate 分 tab 展示，每个场次含 projects 列表。")
    public ApiResponse<List<FinalScheduleSession>> getSessionSchedule(@RequestParam Long competitionId) {
        return ApiResponse.ok(finalService.getSessionSchedule(competitionId));
    }

    // ── 专场内项目列表 ────────────────────────────────────────────────────────

    @GetMapping("/sessions/{sessionCode}/projects")
    @Operation(summary = "获取专场内项目列表", description = "按上台顺序返回该专场所有项目")
    public ApiResponse<List<FinalProjectItem>> listProjects(
            @RequestParam Long competitionId,
            @PathVariable String sessionCode) {
        return ApiResponse.ok(finalService.listProjectsBySession(competitionId, sessionCode));
    }

    // ── 分配评委到专场 ────────────────────────────────────────────────────────

    @PostMapping("/sessions/{sessionCode}/assign-reviewer")
    @Operation(summary = "分配评委到专场", description = "将一名评委分配到该专场下的所有项目（创建 FINAL 阶段 ReviewTask）")
    public ApiResponse<String> assignReviewer(
            @RequestParam Long competitionId,
            @PathVariable String sessionCode,
            @RequestParam Long reviewerId) {
        requireAdminRole();
        String msg = finalService.assignReviewerToSession(competitionId, sessionCode, reviewerId);
        return ApiResponse.ok(msg);
    }

    // ── 评分汇总 ──────────────────────────────────────────────────────────────

    @GetMapping("/scores")
    @Operation(summary = "评分汇总（管理侧）",
               description = "查看指定竞赛/专场的所有评分任务与评分结果。" +
                             "OPERATOR 角色只能查看其被分配的会场；ADMIN/OPS 可查所有。")
    public ApiResponse<List<FinalTaskItem>> scoreSummary(
            @RequestParam Long competitionId,
            @RequestParam(required = false) String sessionCode) {
        String role = getCurrentRole();
        if ("OPERATOR".equals(role)) {
            Long staffId = getCurrentUserId();
            List<String> assignedSessions = staffSessionRepo.findByStaffId(staffId)
                    .stream().map(StaffSessionAssignment::getSessionCode).collect(Collectors.toList());
            if (sessionCode != null && !assignedSessions.contains(sessionCode)) {
                throw new ResponseStatusException(HttpStatus.FORBIDDEN, "无权查看该会场");
            }
            if (sessionCode == null) {
                return ApiResponse.ok(assignedSessions.stream()
                        .flatMap(sc -> finalService.adminScoreSummary(competitionId, sc).stream())
                        .collect(Collectors.toList()));
            }
        }
        return ApiResponse.ok(finalService.adminScoreSummary(competitionId, sessionCode));
    }

    // ── 按评委查询任务 ────────────────────────────────────────────────────────

    @GetMapping("/reviewer-tasks")
    @Operation(summary = "按评委查询现场竞赛任务",
               description = "返回指定评委在该竞赛中的所有现场竞赛任务（含打分状态和得分）。" +
                       "reviewerId 和 reviewerName 至少传一个；两者同时传时以 reviewerId 优先。" +
                       "OPERATOR 只能查询其负责会场内的评委任务；ADMIN/OPS 无限制。")
    public ApiResponse<List<FinalTaskItem>> reviewerTasks(
            @RequestParam Long competitionId,
            @RequestParam(required = false) Long reviewerId,
            @RequestParam(required = false) String reviewerName) {
        String role = getCurrentRole();
        List<String> allowedSessions = null;
        if ("OPERATOR".equals(role)) {
            Long staffId = getCurrentUserId();
            allowedSessions = staffSessionRepo.findByStaffId(staffId)
                    .stream().map(StaffSessionAssignment::getSessionCode).collect(Collectors.toList());
        } else {
            requireAdminRole();
        }
        return ApiResponse.ok(finalService.adminScoreSummaryByReviewer(
                competitionId, reviewerId, reviewerName, allowedSessions));
    }

    // ── 驳回评分（OPERATOR/ADMIN）────────────────────────────────────────────

    @PostMapping("/scores/{taskId}/reject")
    @Transactional
    @Operation(summary = "驳回评分",
               description = "将已提交（SCORED）或草稿（DRAFT）的评分任务驳回为 PENDING，清除评分内容。" +
                             "OPERATOR 只能驳回其负责会场的任务；ADMIN/OPS 无限制。")
    public ApiResponse<String> rejectScore(@PathVariable Long taskId) {
        ReviewTask task = reviewTaskRepository.findById(taskId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "任务不存在"));

        String role = getCurrentRole();
        if ("OPERATOR".equals(role)) {
            Long staffId = getCurrentUserId();
            String sessionCode = task.getRegistration() != null
                    ? task.getRegistration().getFinalSessionCode() : null;
            if (sessionCode == null || !staffSessionRepo.existsByStaffIdAndSessionCode(staffId, sessionCode)) {
                throw new ResponseStatusException(HttpStatus.FORBIDDEN, "无权驳回该会场的评分");
            }
        }

        if (task.getStatus() != ReviewStatus.SCORED && task.getStatus() != ReviewStatus.DRAFT) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "该任务当前状态不可驳回");
        }

        reviewScoreRepository.findByReviewTaskId(taskId).ifPresent(reviewScoreRepository::delete);
        task.setStatus(ReviewStatus.PENDING);
        task.setUpdatedAt(java.time.LocalDateTime.now());
        reviewTaskRepository.save(task);

        return ApiResponse.ok("驳回成功，任务已重置为待评分状态");
    }

    // ── 计算排名 ──────────────────────────────────────────────────────────────

    @PostMapping("/compute-ranking")
    @Operation(summary = "计算现场竞赛排名",
               description = "幂等接口：先清空旧快照，以专场为单位直接均分计算排名并持久化")
    public ApiResponse<String> computeRanking(@RequestParam Long competitionId) {
        requireAdminRole();
        return ApiResponse.ok(finalService.computeRanking(competitionId));
    }

    @PostMapping("/compute-total-ranking")
    @Operation(summary = "计算综合总分排名",
               description = "依赖已完成的书审/面谈快照和现场竞赛快照，" +
                       "按 书审D*40%+现场均分*60% 合并总分，专场内排名，结果回写 final_ranking_snapshots")
    public ApiResponse<String> computeTotalRanking(@RequestParam Long competitionId) {
        requireAdminRole();
        return ApiResponse.ok(finalService.computeTotalRanking(competitionId));
    }

    // ── 查询排名 ──────────────────────────────────────────────────────────────

    @GetMapping("/ranking")
    @Operation(summary = "查询现场竞赛排名",
               description = "返回最近一次计算的排名结果；sessionCode 不传则返回全部专场")
    public ApiResponse<List<FinalRankingItem>> getRanking(
            @RequestParam Long competitionId,
            @RequestParam(required = false) String sessionCode) {
        return ApiResponse.ok(finalService.getRanking(competitionId, sessionCode));
    }

    // ── 全局混合排名 ──────────────────────────────────────────────────────────

    @GetMapping("/ranking/mixed")
    @Operation(summary = "全局混合排名",
               description = "所有专场项目汇总到一起，按去极值均分统一降序排名，不区分专场")
    public ApiResponse<List<FinalRankingItem>> getMixedRanking(@RequestParam Long competitionId) {
        return ApiResponse.ok(finalService.getMixedRanking(competitionId));
    }

    // ── 导出排名 Excel ────────────────────────────────────────────────────────

    @GetMapping("/ranking/export")
    @Operation(summary = "导出现场竞赛排名 Excel",
               description = "下载排名结果 xlsx；sessionCode 不传则导出全部专场")
    public void exportRanking(
            @RequestParam Long competitionId,
            @RequestParam(required = false) String sessionCode,
            HttpServletResponse response) throws IOException, Exception {
        byte[] bytes = finalService.exportRankingExcel(competitionId, sessionCode);
        String filename = URLEncoder.encode("现场竞赛排名.xlsx", StandardCharsets.UTF_8.name());
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + filename);
        response.getOutputStream().write(bytes);
    }

    // ── 工具方法 ──────────────────────────────────────────────────────────────

    private Long getCurrentUserId() {
        Object userId = request.getAttribute("userId");
        if (userId == null) throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "未登录");
        return Long.parseLong(userId.toString());
    }

    private String getCurrentRole() {
        Object role = request.getAttribute("role");
        return role != null ? role.toString() : "";
    }

    private void requireAdminRole() {
        String role = getCurrentRole();
        if (!"ADMIN".equals(role) && !"OPS".equals(role) && !"COMMITTEE_ADMIN".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "无权限");
        }
    }
}
