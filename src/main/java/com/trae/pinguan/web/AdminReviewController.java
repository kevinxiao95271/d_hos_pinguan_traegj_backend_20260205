package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.entity.ScoringSnapshot;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import com.trae.pinguan.service.ComputeJobTracker;
import com.trae.pinguan.service.ComputeRankingAsyncService;
import com.trae.pinguan.service.ReviewService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.ComputeJobResponse;
import com.trae.pinguan.web.dto.ComputeRankingRequest;
import com.trae.pinguan.web.dto.ProjectFeedbackFilterOptionsResponse;
import com.trae.pinguan.web.dto.ProjectFeedbackItem;
import com.trae.pinguan.web.dto.ProjectFeedbackUpdateRequest;
import com.trae.pinguan.web.dto.ReviewAutoAssignRequest;
import com.trae.pinguan.web.dto.ReviewFeedbackItem;
import com.trae.pinguan.web.dto.ReviewRankingItem;
import com.trae.pinguan.web.dto.ReviewSummaryItem;
import com.trae.pinguan.web.dto.ReviewTaskAssignRequest;
import com.trae.pinguan.web.dto.ReviewScoreReturnRequest;
import com.trae.pinguan.web.dto.ScoreExportRow;
import com.trae.pinguan.web.dto.ScoreListItem;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import javax.servlet.http.HttpServletResponse;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.CellStyle;
import org.apache.poi.ss.usermodel.FillPatternType;
import org.apache.poi.ss.usermodel.Font;
import org.apache.poi.ss.usermodel.IndexedColors;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/admin/reviews")
@RequiredArgsConstructor
@Tag(name = "后台评审")
@SecurityRequirement(name = "BearerAuth")
public class AdminReviewController {
    private final ReviewService reviewService;
    private final com.trae.pinguan.service.ReviewerService reviewerService;
    private final ComputeRankingAsyncService computeRankingAsyncService;
    private final ComputeJobTracker computeJobTracker;
    private final javax.servlet.http.HttpServletRequest request;

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
    @Operation(summary = "后台评分汇总",
               description = "reviewerName 不传则返回所有项目；传入时仅返回含该评委任务的项目")
    public ApiResponse<List<ReviewSummaryItem>> summary(@RequestParam Long competitionId,
                                                        @RequestParam ReviewStage stage,
                                                        @RequestParam(required = false) String reviewerName) {
        return ApiResponse.ok(reviewService.summaryByStage(competitionId, stage, reviewerName));
    }

    @PostMapping("/compute-ranking")
    @Operation(summary = "触发系数调整排名计算（异步，立即返回 jobId）",
            description = "任务在后台异步执行，立即返回 jobId。" +
                    "前端每隔 2 秒轮询 GET /compute-ranking/status?jobId=xxx，" +
                    "status=SUCCESS 时排名已写入快照可供查询。\n" +
                    "interviewOnly=true 时：进阶组跳过书审合分，纯面谈系数路径，快照存入 INTERVIEW_ONLY stage。")
    public ApiResponse<ComputeJobResponse> computeRanking(@Valid @RequestBody ComputeRankingRequest request) {
        String jobId = UUID.randomUUID().toString().replace("-", "").substring(0, 16);
        computeJobTracker.start(jobId);
        computeRankingAsyncService.compute(
                jobId, request.getCompetitionId(), request.getStage(),
                request.getGroupType(), request.isInterviewOnly());
        return ApiResponse.ok(ComputeJobResponse.builder()
                .jobId(jobId)
                .status("RUNNING")
                .build());
    }

    @GetMapping("/compute-ranking/status")
    @Operation(summary = "查询算分任务状态",
            description = "轮询此接口，status=RUNNING 时继续等待；SUCCESS 时可查询排名；FAILED 时查看 error 字段。")
    public ApiResponse<ComputeJobResponse> computeRankingStatus(@RequestParam String jobId) {
        return computeJobTracker.get(jobId)
                .map(info -> ApiResponse.ok(ComputeJobResponse.builder()
                        .jobId(jobId)
                        .status(info.getStatus().name())
                        .snapshotCount(info.getSnapshotCount())
                        .error(info.getError())
                        .startedAt(info.getStartedAt())
                        .finishedAt(info.getFinishedAt())
                        .progress(info.getProgress())
                        .progressMsg(info.getProgressMsg())
                        .build()))
                .orElse(ApiResponse.fail("job not found: " + jobId));
    }

    @GetMapping("/rankings")
    @Operation(summary = "后台评分排名（优先读快照，无快照则实时计算均分）")
    public ApiResponse<List<ReviewRankingItem>> rankings(@RequestParam Long competitionId,
                                                         @RequestParam ReviewStage stage,
                                                         @RequestParam(required = false) GroupType groupType) {
        return ApiResponse.ok(reviewService.rankingFromSnapshot(competitionId, stage, groupType));
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

    @GetMapping("/project-feedback")
    @Operation(summary = "后台项目意见汇总",
            description = "按项目汇总已提交评委的亮点与不足；返回时会刷新原始汇总，但不覆盖组委会编辑稿。" +
                    "支持按组别、分组、项目名、机构名、发布状态筛选。")
    public ApiResponse<List<ProjectFeedbackItem>> projectFeedback(
            @RequestParam Long competitionId,
            @RequestParam(defaultValue = "BOOK") ReviewStage stage,
            @RequestParam(required = false) GroupType groupType,
            @RequestParam(required = false) String groupCode,
            @RequestParam(required = false) String projectName,
            @RequestParam(required = false) String institutionName,
            @RequestParam(required = false) Boolean published,
            @RequestParam(defaultValue = "false") boolean refresh) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewService.projectFeedbacksByStage(
                competitionId, stage, groupType, groupCode, projectName, institutionName, published, refresh));
    }

    @GetMapping("/project-feedback/filter-options")
    @Operation(summary = "项目意见筛选项（组别-分组联动）",
            description = "返回组别列表及组别对应分组列表。传 groupType 时，groupCodes 返回该组别下分组；不传则返回全部分组。")
    public ApiResponse<ProjectFeedbackFilterOptionsResponse> projectFeedbackFilterOptions(
            @RequestParam Long competitionId,
            @RequestParam(defaultValue = "BOOK") ReviewStage stage,
            @RequestParam(required = false) GroupType groupType) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewService.projectFeedbackFilterOptions(competitionId, stage, groupType));
    }

    @PutMapping("/project-feedback/batch")
    @Operation(summary = "批量保存项目意见草稿",
            description = "一次性保存多个项目的组委会编辑稿（亮点/不足），语义与单条 PUT 完全一致。" +
                    "单次请求最多 200 条；超出限制返回 400。不触发发布，仅保存草稿。")
    public ApiResponse<List<ProjectFeedbackItem>> batchUpdateProjectFeedback(
            @RequestParam(defaultValue = "BOOK") ReviewStage stage,
            @Valid @RequestBody com.trae.pinguan.web.dto.ProjectFeedbackBatchUpdateRequest body) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewService.batchUpdateProjectFeedback(stage, body.getItems(), getCurrentUserId()));
    }

    @PutMapping("/project-feedback/{registrationId}")
    @Operation(summary = "后台编辑项目意见汇总")    public ApiResponse<ProjectFeedbackItem> updateProjectFeedback(
            @PathVariable Long registrationId,
            @RequestParam(defaultValue = "BOOK") ReviewStage stage,
            @Valid @RequestBody ProjectFeedbackUpdateRequest body) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewService.updateProjectFeedback(
                registrationId, stage, body, getCurrentUserId()));
    }

    @GetMapping("/project-feedback/export")
    @Operation(summary = "导出项目意见反馈为 Excel",
            description = "将当前筛选条件下的所有项目意见（亮点/不足原始汇总、组委会编辑稿、最终稿）导出为 .xlsx 文件。" +
                    "支持与列表页相同的筛选参数：groupType / groupCode / projectName / institutionName / published。")
    public void exportProjectFeedback(
            @RequestParam Long competitionId,
            @RequestParam(defaultValue = "BOOK") ReviewStage stage,
            @RequestParam(required = false) GroupType groupType,
            @RequestParam(required = false) String groupCode,
            @RequestParam(required = false) String projectName,
            @RequestParam(required = false) String institutionName,
            @RequestParam(required = false) Boolean published,
            HttpServletResponse response) throws IOException {
        requireCommitteeOrOps();
        List<ProjectFeedbackItem> items = reviewService.projectFeedbacksByStage(
                competitionId, stage, groupType, groupCode, projectName, institutionName, published, false);

        String stageName = ReviewStage.BOOK == stage ? "书审" : "面谈";
        String filename = URLEncoder.encode("项目意见反馈-" + stageName + ".xlsx", StandardCharsets.UTF_8.name());
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + filename);

        try (Workbook wb = new XSSFWorkbook()) {
            Sheet sheet = wb.createSheet(stageName + "项目意见反馈");

            CellStyle headerStyle = wb.createCellStyle();
            headerStyle.setFillForegroundColor(IndexedColors.CORNFLOWER_BLUE.getIndex());
            headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
            Font headerFont = wb.createFont();
            headerFont.setBold(true);
            headerFont.setColor(IndexedColors.WHITE.getIndex());
            headerStyle.setFont(headerFont);

            CellStyle wrapStyle = wb.createCellStyle();
            wrapStyle.setWrapText(true);

            String[] headers = {
                "项目编号", "项目名称", "医院名称", "组别", "小组",
                "评委原始亮点汇总", "评委原始不足汇总",
                "最终亮点（组委会已编辑则用编辑稿，否则用原始汇总）",
                "最终不足（组委会已编辑则用编辑稿，否则用原始汇总）",
                "是否已发布", "最后修改时间", "发布时间"
            };
            Row headerRow = sheet.createRow(0);
            for (int i = 0; i < headers.length; i++) {
                Cell c = headerRow.createCell(i);
                c.setCellValue(headers[i]);
                c.setCellStyle(headerStyle);
            }

            int rowIdx = 1;
            for (ProjectFeedbackItem item : items) {
                Row row = sheet.createRow(rowIdx++);
                int col = 0;
                row.createCell(col++).setCellValue(item.getRegistrationId() != null ? item.getRegistrationId() : 0L);
                row.createCell(col++).setCellValue(item.getProjectName() != null ? item.getProjectName() : "");
                row.createCell(col++).setCellValue(item.getInstitutionName() != null ? item.getInstitutionName() : "");
                row.createCell(col++).setCellValue(groupTypeLabel(item.getGroupType()));
                row.createCell(col++).setCellValue(item.getGroupCode() != null ? item.getGroupCode() : "");

                setWrappedText(row, col++, item.getSourceHighlight(), wrapStyle);
                setWrappedText(row, col++, item.getSourceWeakness(), wrapStyle);
                setWrappedText(row, col++, item.getFinalHighlight(), wrapStyle);
                setWrappedText(row, col++, item.getFinalWeakness(), wrapStyle);

                row.createCell(col++).setCellValue(item.isPublished() ? "是" : "否");
                row.createCell(col++).setCellValue(item.getUpdatedAt() != null ? item.getUpdatedAt().toString() : "");
                row.createCell(col++).setCellValue(item.getPublishedAt() != null ? item.getPublishedAt().toString() : "");
            }

            for (int i = 0; i < headers.length; i++) {
                sheet.autoSizeColumn(i);
            }

            wb.write(response.getOutputStream());
        }
    }

    private void setWrappedText(Row row, int col, String value, CellStyle wrapStyle) {
        Cell c = row.createCell(col);
        c.setCellValue(value != null ? value : "");
        c.setCellStyle(wrapStyle);
    }

    @PostMapping("/project-feedback/{registrationId}/publish")
    @Operation(summary = "发布或撤回单个项目意见")
    public ApiResponse<ProjectFeedbackItem> publishProjectFeedback(
            @PathVariable Long registrationId,
            @RequestParam(defaultValue = "BOOK") ReviewStage stage,
            @RequestParam(defaultValue = "true") boolean published) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewService.publishProjectFeedback(
                registrationId, stage, published, getCurrentUserId()));
    }

    @PostMapping("/project-feedback/publish")
    @Operation(summary = "批量发布或撤回项目意见")
    public ApiResponse<List<ProjectFeedbackItem>> publishProjectFeedbacks(
            @RequestParam Long competitionId,
            @RequestParam(defaultValue = "BOOK") ReviewStage stage,
            @RequestParam(defaultValue = "true") boolean published) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewService.publishProjectFeedbacks(
                competitionId, stage, published, getCurrentUserId()));
    }

    @PostMapping("/scores/return")
    @Operation(summary = "后台退回书审评分")
    public ApiResponse<ReviewTask> returnScore(@Valid @RequestBody ReviewScoreReturnRequest request) {
        return ApiResponse.ok(reviewService.returnScore(request));
    }

    @PostMapping("/interview-scores/return")
    @Operation(summary = "后台退回面谈评分")
    public ApiResponse<Void> returnInterviewScore(@RequestParam Long reviewTaskId) {
        reviewService.returnInterviewScore(reviewTaskId);
        return ApiResponse.ok(null);
    }

    @GetMapping("/interview-summary")
    @Operation(summary = "面谈打分汇总（各评委得分 + 均分）")
    public ApiResponse<List<java.util.Map<String, Object>>> interviewSummary(
            @RequestParam Long competitionId) {
        return ApiResponse.ok(reviewService.interviewSummaryByCompetition(competitionId));
    }

    @GetMapping("/score-list")
    @Operation(summary = "得分明细列表（书审 / 面谈通用）",
               description = "用 stage=BOOK 查书审得分列表，stage=INTERVIEW 查面谈得分列表。" +
                             "每条记录含项目信息（机构等级、分组）及每位评委的维度得分和打分状态。" +
                             "书审维度：plan/problem/action/success/review/operation/presentation。" +
                             "面谈维度：topic/process/interviewOperation/result。\n" +
                             "可选筛选参数：\n" +
                             "- groupType：按组别过滤（BASIC / COMPREHENSIVE / ADVANCED）\n" +
                             "- reviewerStatus：只返回含指定状态评委的项目（PENDING/DRAFT/SCORED/RETURNED/RECUSED）\n" +
                             "- keyword：按项目名称或机构名称模糊搜索（不区分大小写）\n" +
                             "- reviewerName：按评委姓名精准匹配（完整姓名，只返回含该评委的项目）")
    public ApiResponse<List<ScoreListItem>> scoreList(
            @RequestParam Long competitionId,
            @RequestParam ReviewStage stage,
            @RequestParam(required = false) GroupType groupType,
            @RequestParam(required = false) ReviewStatus reviewerStatus,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String reviewerName) {
        return ApiResponse.ok(reviewService.scoreListByStage(competitionId, stage, groupType, reviewerStatus, keyword, reviewerName));
    }

    @GetMapping("/score-export")
    @Operation(summary = "导出打分快照为 Excel",
               description = "需先触发 compute-ranking 生成快照，再调用本接口导出。\n" +
                             "stage 可选值：BOOK（书审）、INTERVIEW（面谈合并分，进阶组含书审权重）、INTERVIEW_ONLY（纯面谈标化分）。\n" +
                             "列：排名 / 组别 / 小组 / 项目编号 / 项目名称 / 医院名称 / 评审1..N / " +
                             "平均分 / 小组均分(An) / 全组均分(B) / 系数(Cn) / 调整后分数(D)")
    public void scoreExport(@RequestParam Long competitionId,
                            @RequestParam ReviewStage stage,
                            HttpServletResponse response) throws IOException {
        List<ScoreExportRow> rows = reviewService.buildScoreExportRows(competitionId, stage);

        int maxReviewers = rows.stream()
                .mapToInt(r -> r.getReviewerScores() != null ? r.getReviewerScores().size() : 0)
                .max().orElse(0);

        String stageName;
        if (stage == ReviewStage.BOOK) {
            stageName = "书审";
        } else if (stage == ReviewStage.INTERVIEW_ONLY) {
            stageName = "面谈标化";
        } else {
            stageName = "面谈";
        }
        String filename = URLEncoder.encode("打分数据-" + stageName + ".xlsx", StandardCharsets.UTF_8.name());
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + filename);

        try (Workbook wb = new XSSFWorkbook()) {
            Sheet sheet = wb.createSheet(stageName + "打分数据");

            // 表头样式
            CellStyle headerStyle = wb.createCellStyle();
            headerStyle.setFillForegroundColor(IndexedColors.CORNFLOWER_BLUE.getIndex());
            headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
            Font headerFont = wb.createFont();
            headerFont.setBold(true);
            headerFont.setColor(IndexedColors.WHITE.getIndex());
            headerStyle.setFont(headerFont);

            Row header = sheet.createRow(0);
            int col = 0;
            String[] fixedHeaders = {"排名", "组别", "小组", "项目编号", "项目名称", "医院名称"};
            for (String h : fixedHeaders) {
                Cell c = header.createCell(col++);
                c.setCellValue(h);
                c.setCellStyle(headerStyle);
            }
            for (int i = 1; i <= maxReviewers; i++) {
                Cell c = header.createCell(col++);
                c.setCellValue("评审" + i);
                c.setCellStyle(headerStyle);
            }
            String[] tailHeaders = {"平均分", "小组均分(An)", "全组均分(B)", "系数(Cn)", "调整后分数(D)"};
            for (String h : tailHeaders) {
                Cell c = header.createCell(col++);
                c.setCellValue(h);
                c.setCellStyle(headerStyle);
            }

            // 数字格式
            CellStyle numStyle = wb.createCellStyle();
            numStyle.setDataFormat(wb.createDataFormat().getFormat("0.00"));

            // 数据行
            int rowIdx = 1;
            for (ScoreExportRow r : rows) {
                Row row = sheet.createRow(rowIdx++);
                col = 0;
                row.createCell(col++).setCellValue(r.getIrank() != null ? r.getIrank() : 0);
                row.createCell(col++).setCellValue(groupTypeLabel(r.getGroupType()));
                row.createCell(col++).setCellValue(r.getGroupCode() != null ? r.getGroupCode() : "");
                row.createCell(col++).setCellValue(r.getRegistrationId() != null ? r.getRegistrationId() : 0L);
                row.createCell(col++).setCellValue(r.getProjectName() != null ? r.getProjectName() : "");
                row.createCell(col++).setCellValue(r.getInstitutionName() != null ? r.getInstitutionName() : "");
                List<Double> scores = r.getReviewerScores() != null ? r.getReviewerScores() : Collections.emptyList();
                for (int i = 0; i < maxReviewers; i++) {
                    Cell c = row.createCell(col++);
                    if (i < scores.size() && scores.get(i) != null) {
                        c.setCellValue(scores.get(i));
                        c.setCellStyle(numStyle);
                    }
                }
                setNum(row, col++, r.getRawAvg(), numStyle);
                setNum(row, col++, r.getGroupAvg(), numStyle);
                setNum(row, col++, r.getOverallAvg(), numStyle);
                setNum(row, col++, r.getCoefficient(), numStyle);
                setNum(row, col++, r.getAdjustedScore(), numStyle);
            }

            // 自适应列宽（跳过评审N列，内容短）
            int totalCols = 6 + maxReviewers + 5;
            for (int i = 0; i < totalCols; i++) {
                sheet.autoSizeColumn(i);
            }

            wb.write(response.getOutputStream());
        }
    }

    private String groupTypeLabel(com.trae.pinguan.domain.enums.GroupType gt) {
        if (gt == null) return "";
        switch (gt) {
            case BASIC:         return "基层组";
            case COMPREHENSIVE: return "综合组";
            case ADVANCED:      return "进阶组";
            default:            return gt.name();
        }
    }

    private void setNum(Row row, int col, Double val, CellStyle style) {
        Cell c = row.createCell(col);
        if (val != null) {
            c.setCellValue(val);
            c.setCellStyle(style);
        }
    }

    private void requireCommitteeOrOps() {
        String role = String.valueOf(request.getAttribute("role"));
        if (!"COMMITTEE".equals(role) && !"COMMITTEE_ADMIN".equals(role) && !"OPS".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "无权限");
        }
    }

    private Long getCurrentUserId() {
        Object userId = request.getAttribute("userId");
        if (userId == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "未登录");
        }
        return Long.parseLong(userId.toString());
    }
}
