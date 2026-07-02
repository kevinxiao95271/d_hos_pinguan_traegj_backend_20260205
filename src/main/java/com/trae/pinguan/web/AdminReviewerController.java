package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.ReviewerInstitutionChange;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.service.JwtService;
import com.trae.pinguan.service.ReviewerService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.ChangeInstitutionRequest;
import com.trae.pinguan.web.dto.ReviewerListItem;
import com.trae.pinguan.web.dto.ReviewerProfileDto;
import com.trae.pinguan.web.dto.ReviewerProfileUpsertRequest;
import com.trae.pinguan.web.dto.ReviewerUpsertRequest;
import com.trae.pinguan.web.dto.ReviewerExportRow;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.io.IOException;
import java.io.InputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
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
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
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
    @Operation(summary = "评委列表",
               description = "传 competitionId 时返回该赛事下每位评委已分配的决赛专场列表（finalSessionCodes）；name 支持姓名模糊搜索")
    public ApiResponse<List<ReviewerListItem>> list(@RequestParam(required = false) Long competitionId,
                                                    @RequestParam(required = false) Long institutionId,
                                                    @RequestParam(required = false) String reviewerGroupCode,
                                                    @RequestParam(required = false) String interviewGroupCode,
                                                    @RequestParam(required = false) String expertBackground,
                                                    @RequestParam(required = false) String name) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.list(competitionId, institutionId, reviewerGroupCode, interviewGroupCode, expertBackground, name));
    }

    @GetMapping("/list")
    @Operation(summary = "评委列表(兼容路径)")
    public ApiResponse<List<ReviewerListItem>> listCompat(@RequestParam(required = false) Long competitionId,
                                                          @RequestParam(required = false) Long institutionId,
                                                          @RequestParam(required = false) String reviewerGroupCode,
                                                          @RequestParam(required = false) String interviewGroupCode,
                                                          @RequestParam(required = false) String expertBackground,
                                                          @RequestParam(required = false) String name) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.list(competitionId, institutionId, reviewerGroupCode, interviewGroupCode, expertBackground, name));
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

    @PutMapping("/{id}/enabled")
    @Operation(summary = "启用或禁用账号（enabled=true/false）",
               description = "将指定账号设置为启用或禁用状态。禁用后该账号无法登录。")
    public ApiResponse<UserAccount> setEnabled(@PathVariable Long id,
                                               @RequestParam boolean enabled) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.setEnabled(id, enabled));
    }

    @PostMapping("/batch-disable")
    @Operation(summary = "批量禁用指定账号",
               description = "必须传 ids（账号 ID 列表），仅禁用指定账号；禁用后账号保留数据但无法登录。")
    public ApiResponse<Integer> batchDisable(@RequestBody java.util.List<Long> ids) {
        requireCommitteeOrOps();
        if (ids == null || ids.isEmpty()) {
            throw new IllegalArgumentException("ids 不能为空");
        }
        int count = reviewerService.batchDisableByIds(ids);
        return ApiResponse.ok(count);
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

    @PutMapping("/{id}/institution")
    @Operation(summary = "管理员修改评委所属机构（记录变更日志）")
    public ApiResponse<Void> changeInstitution(@PathVariable Long id,
                                               @Valid @RequestBody ChangeInstitutionRequest req) {
        requireCommitteeOrOps();
        Long operatorId = Long.parseLong(request.getAttribute("userId").toString());
        String operatorName = (String) request.getAttribute("userName");
        reviewerService.changeInstitution(id, req, operatorId, operatorName);
        return ApiResponse.ok(null);
    }

    @GetMapping("/export")
    @Operation(summary = "批量导出评审专家信息为 Excel",
               description = "传 competitionId 时额外导出「分配场次」列")
    public void export(@RequestParam(required = false) Long competitionId,
                       HttpServletResponse response) throws IOException {
        requireCommitteeOrOps();
        List<ReviewerExportRow> rows = reviewerService.buildExportRows(competitionId);
        String date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String filename = URLEncoder.encode("评审专家_" + date + ".xlsx", StandardCharsets.UTF_8.name());
        response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + filename);

        try (Workbook wb = new XSSFWorkbook()) {
            Sheet sheet = wb.createSheet("评审专家");

            CellStyle headerStyle = wb.createCellStyle();
            headerStyle.setFillForegroundColor(IndexedColors.CORNFLOWER_BLUE.getIndex());
            headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);
            Font headerFont = wb.createFont();
            headerFont.setBold(true);
            headerFont.setColor(IndexedColors.WHITE.getIndex());
            headerStyle.setFont(headerFont);

            String[] headers = {
                "ID", "姓名", "手机号", "职称", "机构",
                "专家背景",
                "性别", "科室", "职务",
                "身份证号", "身份证正面", "身份证背面",
                "开户银行", "银行卡号",
                "专业背景", "专业背景(其他)",
                "熟悉工具", "熟悉工具(其他)",
                "擅长主题", "擅长主题(其他)",
                "品管经验",
                "已提交", "草稿中", "待评审", "已规避",
                "分配决赛场次"
            };
            Row header = sheet.createRow(0);
            for (int i = 0; i < headers.length; i++) {
                Cell c = header.createCell(i);
                c.setCellValue(headers[i]);
                c.setCellStyle(headerStyle);
            }

            int rowIdx = 1;
            for (ReviewerExportRow r : rows) {
                Row row = sheet.createRow(rowIdx++);
                int col = 0;
                row.createCell(col++).setCellValue(r.getUserId() != null ? r.getUserId() : 0L);
                row.createCell(col++).setCellValue(s(r.getName()));
                row.createCell(col++).setCellValue(s(r.getPhone()));
                row.createCell(col++).setCellValue(s(r.getTitle()));
                row.createCell(col++).setCellValue(s(r.getInstitutionName()));
                row.createCell(col++).setCellValue(s(r.getExpertBackground()));
                row.createCell(col++).setCellValue(s(r.getGender()));
                row.createCell(col++).setCellValue(s(r.getDepartment()));
                row.createCell(col++).setCellValue(s(r.getPosition()));
                row.createCell(col++).setCellValue(s(r.getIdNumber()));
                row.createCell(col++).setCellValue(s(r.getIdCardFront()));
                row.createCell(col++).setCellValue(s(r.getIdCardBack()));
                row.createCell(col++).setCellValue(s(r.getBankName()));
                row.createCell(col++).setCellValue(s(r.getBankCardNo()));
                row.createCell(col++).setCellValue(decodeJson(r.getBackgroundsJson(), BACKGROUNDS));
                row.createCell(col++).setCellValue(s(r.getBackgroundsOther()));
                row.createCell(col++).setCellValue(decodeJson(r.getToolsJson(), TOOLS));
                row.createCell(col++).setCellValue(s(r.getToolsOther()));
                row.createCell(col++).setCellValue(decodeJson(r.getTopicsJson(), TOPICS));
                row.createCell(col++).setCellValue(s(r.getTopicsOther()));
                row.createCell(col++).setCellValue(decodeJson(r.getExperienceJson(), EXPERIENCE));
                row.createCell(col++).setCellValue(r.getTaskScored() != null ? r.getTaskScored() : 0L);
                row.createCell(col++).setCellValue(r.getTaskDraft()  != null ? r.getTaskDraft()  : 0L);
                row.createCell(col++).setCellValue(r.getTaskPending()!= null ? r.getTaskPending(): 0L);
                row.createCell(col++).setCellValue(r.getTaskRecused()!= null ? r.getTaskRecused(): 0L);
                row.createCell(col).setCellValue(s(r.getFinalSessionCodes()));
            }
            for (int i = 0; i < headers.length; i++) sheet.autoSizeColumn(i);
            wb.write(response.getOutputStream());
        }
    }

    private static String s(String v) { return v != null ? v : ""; }

    // ── JSON 枚举解码 ─────────────────────────────────────────
    private static final java.util.Map<String, String> BACKGROUNDS = new java.util.LinkedHashMap<>();
    private static final java.util.Map<String, String> TOOLS       = new java.util.LinkedHashMap<>();
    private static final java.util.Map<String, String> TOPICS      = new java.util.LinkedHashMap<>();
    private static final java.util.Map<String, String> EXPERIENCE  = new java.util.LinkedHashMap<>();
    static {
        BACKGROUNDS.put("MEDICAL",           "医疗");
        BACKGROUNDS.put("NURSING",           "护理");
        BACKGROUNDS.put("PHARMACY",          "药学");
        BACKGROUNDS.put("MEDICAL_TECHNOLOGY","医技");
        BACKGROUNDS.put("MANAGEMENT",        "管理");
        BACKGROUNDS.put("QUALITY_MGMT",      "质量管理");
        BACKGROUNDS.put("QUALITY_MANAGEMENT","质量管理");
        BACKGROUNDS.put("OTHER",             "其他");

        TOOLS.put("PDCA",        "PDCA");
        TOOLS.put("FOCUS_PDCA",  "FOCUS-PDCA");
        TOOLS.put("QCC_PROBLEM", "品管圈-问题解决");
        TOOLS.put("QCC_TOPIC",   "品管圈-课题达成");
        TOOLS.put("QFD",         "QFD");
        TOOLS.put("FMEA",        "FMEA");
        TOOLS.put("RCA",         "根本原因分析");
        TOOLS.put("SIX_SIGMA",   "六西格玛");
        TOOLS.put("5S",          "5S");
        TOOLS.put("LEAN",        "精益管理");
        TOOLS.put("OTHER",       "其他");

        TOPICS.put("PATIENT_CARE",           "病人照护");
        TOPICS.put("MEDICAL_QUALITY_SAFETY", "医疗质量与安全");
        TOPICS.put("MEDICAL_QUALITY",        "医疗质量");
        TOPICS.put("MEDICAL_RECORDS",        "病历质量");
        TOPICS.put("TIME_EFFICIENCY",        "时间效率");
        TOPICS.put("COST_EFFICIENCY",        "成本效益");
        TOPICS.put("SAFETY_ENV",             "安全环境");
        TOPICS.put("SATISFACTION",           "满意度");
        TOPICS.put("EDUCATION",              "教育训练");
        TOPICS.put("PROCESS",                "流程改造");
        TOPICS.put("OTHER",                  "其他");

        EXPERIENCE.put("PROJECT_LEADER",   "担任过品管项目负责人");
        EXPERIENCE.put("COACHED_PROJECT",  "辅导过品管参赛项目");
        EXPERIENCE.put("UNIT_JUDGE",       "单位内品管大赛评委");
        EXPERIENCE.put("CITY_JUDGE",       "市/区/县级品管大赛评委");
        EXPERIENCE.put("PROVINCE_JUDGE",   "省级及以上品管大赛评委");
    }

    /** 将 JSON 数组字符串解码为中文，逗号分隔；未知 key 原样保留 */
    private static String decodeJson(String json, java.util.Map<String, String> labelMap) {
        if (json == null || json.trim().isEmpty()) return "";
        try {
            com.fasterxml.jackson.databind.ObjectMapper om = new com.fasterxml.jackson.databind.ObjectMapper();
            java.util.List<String> keys = om.readValue(json,
                    om.getTypeFactory().constructCollectionType(java.util.List.class, String.class));
            return keys.stream()
                    .map(k -> labelMap.getOrDefault(k, k))
                    .collect(java.util.stream.Collectors.joining("、"));
        } catch (Exception e) {
            return json;
        }
    }

    @GetMapping("/id-cards/download")
    @Operation(summary = "批量打包下载所有评委身份证照片（ZIP）")
    public void downloadIdCardsZip(HttpServletResponse response) throws IOException {
        requireCommitteeOrOps();
        java.util.List<Object[]> entries = reviewerService.listIdCardEntries();
        String date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String filename = URLEncoder.encode("身份证照片_" + date + ".zip", StandardCharsets.UTF_8.name());
        response.setContentType("application/zip");
        response.setHeader("Content-Disposition", "attachment; filename*=UTF-8''" + filename);

        // 同一姓名可能重复，用计数器去重
        java.util.Map<String, Integer> nameCount = new java.util.HashMap<>();
        try (ZipOutputStream zos = new ZipOutputStream(response.getOutputStream())) {
            zos.setLevel(0); // 图片已压缩，不再压缩节省 CPU
            for (Object[] entry : entries) {
                String name     = (String) entry[1];
                String instName = (String) entry[2];
                String frontUrl = (String) entry[3];
                String backUrl  = (String) entry[4];

                // 去除文件名非法字符
                String safeName = (name + "_" + instName).replaceAll("[\\\\/:*?\"<>|]", "_");
                int seq = nameCount.merge(safeName, 1, Integer::sum);
                String prefix = seq > 1 ? safeName + "_" + seq : safeName;

                if (frontUrl != null) {
                    addZipEntry(zos, prefix + "_正面.jpg", frontUrl);
                }
                if (backUrl != null) {
                    addZipEntry(zos, prefix + "_背面.jpg", backUrl);
                }
            }
        }
    }

    private void addZipEntry(ZipOutputStream zos, String entryName, String objectName) {
        try (InputStream is = reviewerService.getIdCardStreamByObjectName(objectName)) {
            zos.putNextEntry(new ZipEntry(entryName));
            byte[] buf = new byte[8192];
            int len;
            while ((len = is.read(buf)) != -1) zos.write(buf, 0, len);
            zos.closeEntry();
        } catch (Exception e) {
            // 单张图片读取失败时跳过，不中断整个 ZIP
        }
    }

    @GetMapping("/{id}/id-card/{side}")
    @Operation(summary = "查看/下载评委身份证图片（side=FRONT 或 BACK）")
    public ResponseEntity<InputStreamResource> viewIdCard(@PathVariable Long id,
                                                          @PathVariable String side) {
        requireCommitteeOrOps();
        InputStream stream = reviewerService.getIdCardStream(id, side);
        return ResponseEntity.ok()
                .contentType(MediaType.IMAGE_JPEG)
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "inline; filename=\"id-card-" + id + "-" + side.toLowerCase() + ".jpg\"")
                .body(new InputStreamResource(stream));
    }

    @GetMapping("/{id}/institution/history")
    @Operation(summary = "查看评委机构变更记录")
    public ApiResponse<List<ReviewerInstitutionChange>> institutionHistory(@PathVariable Long id) {
        requireCommitteeOrOps();
        return ApiResponse.ok(reviewerService.getInstitutionHistory(id));
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
