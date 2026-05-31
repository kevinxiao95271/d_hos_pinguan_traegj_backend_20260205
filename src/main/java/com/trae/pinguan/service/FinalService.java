package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.FinalRankingSnapshot;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.ReviewScore;
import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import com.trae.pinguan.repository.FinalRankingSnapshotRepository;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.repository.ReviewScoreRepository;
import com.trae.pinguan.repository.ReviewTaskRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.FinalProjectItem;
import com.trae.pinguan.web.dto.FinalRankingItem;
import com.trae.pinguan.web.dto.FinalScoreItem;
import com.trae.pinguan.web.dto.FinalScoreRequest;
import com.trae.pinguan.web.dto.FinalScheduleSession;
import com.trae.pinguan.web.dto.FinalSessionItem;
import com.trae.pinguan.web.dto.FinalTaskItem;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.CellStyle;
import org.apache.poi.ss.usermodel.CellType;
import org.apache.poi.ss.usermodel.FillPatternType;
import org.apache.poi.ss.usermodel.Font;
import org.apache.poi.ss.usermodel.IndexedColors;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;

@Service
@RequiredArgsConstructor
public class FinalService {

    private final RegistrationRepository registrationRepository;
    private final ReviewTaskRepository reviewTaskRepository;
    private final ReviewScoreRepository reviewScoreRepository;
    private final UserAccountRepository userAccountRepository;
    private final FinalRankingSnapshotRepository finalRankingSnapshotRepository;

    // ── 导入专场分组 ──────────────────────────────────────────────────────────

    /**
     * 解析 xlsx，以「项目编号（registration.id）」匹配，
     * 批量写入 finalSessionCode / finalSessionOrder / finalScoreForm。
     * 跳过：header 行、项目编号为空或非数字的行。
     */
    @Transactional
    public String importSessions(Long competitionId, MultipartFile file) throws Exception {
        List<Registration> allRegs = registrationRepository.findByCompetitionId(competitionId);
        Map<Long, Registration> regById = allRegs.stream()
                .collect(Collectors.toMap(Registration::getId, r -> r));

        int updated = 0;
        int skipped = 0;

        try (Workbook wb = new XSSFWorkbook(file.getInputStream())) {
            for (int si = 0; si < wb.getNumberOfSheets(); si++) {
                Sheet sheet = wb.getSheetAt(si);
                // 第一个 sheet 是汇总分数表，跳过
                if (si == 0) continue;

                for (int ri = 1; ri <= sheet.getLastRowNum(); ri++) {
                    Row row = sheet.getRow(ri);
                    if (row == null) continue;

                    // 找 项目编号列（第3列，index=2）和 组别列（第1列，index=0）
                    // sheet 列: 组别/时间, 顺序, 项目编号, 机构名称, 项目名称, 运用工具, 评分表
                    Long regId = getCellLong(row, 2);
                    if (regId == null) {
                        skipped++;
                        continue;
                    }

                    Registration reg = regById.get(regId);
                    if (reg == null) {
                        skipped++;
                        continue;
                    }

                    Integer order = getCellInt(row, 1);
                    String rawForm = getCellString(row, 6);
                    String scoreForm = normalizeScoreForm(rawForm);
                    String sessionCode = getCellString(row, 0);
                    // 部分 sheet 中 sessionCode 列是时间段（如"8:30-9:40"），取组别需从数据行本身获取
                    // 组别名统一从 sheet 名或 row[3]（机构）前的规律读取
                    // 实际上，组别 code 存在于第1行 row[0] 或行数据 row[0]
                    // 如果 sessionCode 看起来是时间段则取 null，后续从 sheet 名推导
                    if (sessionCode != null && sessionCode.matches("\\d+:\\d+.*")) {
                        sessionCode = null;
                    }
                    // fallback: 从 sheet 名提取专场代码（去掉日期和括号）
                    if (sessionCode == null || sessionCode.trim().isEmpty()) {
                        sessionCode = extractSessionCodeFromSheetName(sheet.getSheetName());
                    }

                    reg.setFinalSessionCode(sessionCode);
                    reg.setFinalSessionOrder(order);
                    reg.setFinalScoreForm(scoreForm);
                    updated++;
                }
            }
        }

        registrationRepository.saveAll(allRegs.stream()
                .filter(r -> r.getFinalSessionCode() != null)
                .collect(Collectors.toList()));

        return String.format("导入完成，共更新 %d 条专场分组，跳过 %d 行", updated, skipped);
    }

    // ── 专场列表 ──────────────────────────────────────────────────────────────

    public List<FinalSessionItem> listSessions(Long competitionId) {
        List<Object[]> rows = registrationRepository.findDistinctFinalSessionsByCompetitionId(competitionId);
        List<FinalSessionItem> result = new ArrayList<>();
        for (Object[] row : rows) {
            String date = (String) row[0];
            String code = (String) row[1];
            List<Registration> regs = registrationRepository
                    .findByCompetitionIdAndFinalSessionCode(competitionId, code);
            int qcc = 0, qfd = 0, nonQcc = 0;
            for (Registration r : regs) {
                String f = r.getFinalScoreForm();
                if ("QCC".equals(f)) qcc++;
                else if ("QFD".equals(f)) qfd++;
                else if ("NON_QCC".equals(f)) nonQcc++;
            }
            result.add(new FinalSessionItem(date, code, regs.size(), qcc, qfd, nonQcc));
        }
        return result;
    }

    // ── 专场项目列表 ──────────────────────────────────────────────────────────

    public List<FinalProjectItem> listProjectsBySession(Long competitionId, String sessionCode) {
        return registrationRepository
                .findByCompetitionIdAndFinalSessionCode(competitionId, sessionCode)
                .stream()
                .map(r -> FinalProjectItem.builder()
                        .registrationId(r.getId())
                        .sessionOrder(r.getFinalSessionOrder())
                        .projectName(r.getProjectName())
                        .institutionName(r.getInstitution() != null ? r.getInstitution().getName() : "")
                        .groupCode(r.getGroupCode())
                        .scoreForm(r.getFinalScoreForm())
                        .build())
                .collect(Collectors.toList());
    }

    // ── 分配评委 ──────────────────────────────────────────────────────────────

    /**
     * 给某个专场的所有项目批量分配一名评委（新建 FINAL 阶段 task）。
     * 若该评委已有该项目的 FINAL task，跳过（幂等）。
     */
    @Transactional
    public String assignReviewerToSession(Long competitionId, String sessionCode, Long reviewerId) {
        UserAccount reviewer = userAccountRepository.findById(reviewerId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "评委不存在"));

        List<Registration> regs = registrationRepository
                .findByCompetitionIdAndFinalSessionCode(competitionId, sessionCode);
        if (regs.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "专场不存在或无项目");
        }

        List<Long> regIds = regs.stream().map(Registration::getId).collect(Collectors.toList());
        List<ReviewTask> existingTasks = reviewTaskRepository.findByReviewerIdAndStage(reviewerId, ReviewStage.FINAL);
        java.util.Set<Long> existingRegIds = existingTasks.stream()
                .map(t -> t.getRegistration().getId())
                .collect(Collectors.toSet());

        LocalDateTime now = LocalDateTime.now();
        List<ReviewTask> toCreate = new ArrayList<>();
        for (Registration reg : regs) {
            if (existingRegIds.contains(reg.getId())) continue;
            ReviewTask task = ReviewTask.builder()
                    .stage(ReviewStage.FINAL)
                    .registration(reg)
                    .reviewer(reviewer)
                    .status(ReviewStatus.PENDING)
                    .createdAt(now)
                    .build();
            toCreate.add(task);
        }

        reviewTaskRepository.saveAll(toCreate);
        return String.format("分配完成，新建 %d 个任务（跳过 %d 个已存在）",
                toCreate.size(), regs.size() - toCreate.size());
    }

    // ── 评委：我的任务 ────────────────────────────────────────────────────────

    @Transactional(readOnly = true)
    public List<FinalTaskItem> myFinalTasks(Long reviewerId) {
        List<ReviewTask> tasks = reviewTaskRepository.findByReviewerIdAndStage(reviewerId, ReviewStage.FINAL);
        if (tasks.isEmpty()) return new ArrayList<>();

        List<Long> taskIds = tasks.stream().map(ReviewTask::getId).collect(Collectors.toList());
        Map<Long, ReviewScore> scoreByTaskId = reviewScoreRepository.findByReviewTaskIdIn(taskIds)
                .stream().collect(Collectors.toMap(ReviewScore::getReviewTaskId, s -> s));

        return tasks.stream().map(t -> {
            Registration reg = t.getRegistration();
            ReviewScore score = scoreByTaskId.get(t.getId());
            UserAccount reviewer = t.getReviewer();
            return FinalTaskItem.builder()
                    .taskId(t.getId())
                    .registrationId(reg.getId())
                    .sessionCode(reg.getFinalSessionCode())
                    .sessionOrder(reg.getFinalSessionOrder())
                    .projectName(reg.getProjectName())
                    .institutionName(reg.getInstitution() != null ? reg.getInstitution().getName() : "")
                    .groupCode(reg.getGroupCode())
                    .scoreForm(reg.getFinalScoreForm())
                    .reviewerId(reviewer != null ? reviewer.getId() : null)
                    .reviewerName(reviewer != null ? reviewer.getName() : null)
                    .reviewerPhone(reviewer != null ? reviewer.getPhone() : null)
                    .status(t.getStatus().name())
                    .total(score != null ? score.getTotal() : null)
                    .scoreItems(buildScoreItems(score))
                    .draftScore(score != null ? toScoreRequest(score) : null)
                    .build();
        }).sorted((a, b) -> {
            // 按 sessionCode + sessionOrder 排序
            int c = compareNullable(a.getSessionCode(), b.getSessionCode());
            if (c != 0) return c;
            return compareNullable(a.getSessionOrder(), b.getSessionOrder());
        }).collect(Collectors.toList());
    }

    // ── 评委：保存/提交评分 ───────────────────────────────────────────────────

    @Transactional
    public void saveScore(Long taskId, Long reviewerId, FinalScoreRequest req, boolean submit) {
        ReviewTask task = reviewTaskRepository.findById(taskId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "任务不存在"));
        if (!task.getReviewer().getId().equals(reviewerId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "无权操作该任务");
        }
        if (task.getStage() != ReviewStage.FINAL) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "该任务非现场评分任务");
        }
        if (task.getStatus() == ReviewStatus.SCORED && submit) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "该任务已提交，不可重复提交");
        }

        ReviewScore score = reviewScoreRepository.findByReviewTaskId(taskId)
                .orElse(ReviewScore.builder().reviewTask(task).build());

        score.setScoreForm(req.getScoreForm());
        score.setPlan(req.getPlan());
        score.setProblem(req.getProblem());
        score.setAction(req.getAction());
        score.setSuccess(req.getSuccess());
        score.setReview(req.getReview());
        score.setOperation(req.getOperation());
        score.setPresentation(req.getPresentation());
        score.setItem8(req.getItem8());
        score.setTotal(computeTotal(req));
        score.setHighlight(req.getHighlight());
        score.setWeakness(req.getWeakness());

        if (submit) {
            score.setSubmittedAt(LocalDateTime.now());
            task.setStatus(ReviewStatus.SCORED);
            task.setUpdatedAt(LocalDateTime.now());
            reviewTaskRepository.save(task);
        } else {
            if (task.getStatus() == ReviewStatus.PENDING || task.getStatus() == ReviewStatus.CONFIRMED) {
                task.setStatus(ReviewStatus.DRAFT);
                task.setUpdatedAt(LocalDateTime.now());
                reviewTaskRepository.save(task);
            }
        }

        reviewScoreRepository.save(score);
    }

    // ── 管理侧：评分汇总 ──────────────────────────────────────────────────────

    @Transactional(readOnly = true)
    public List<FinalTaskItem> adminScoreSummary(Long competitionId, String sessionCode) {
        List<ReviewTask> tasks = sessionCode != null
                ? reviewTaskRepository.findWithDetailsByStageAndCompetitionId(ReviewStage.FINAL, competitionId)
                        .stream()
                        .filter(t -> sessionCode.equals(t.getRegistration().getFinalSessionCode()))
                        .collect(Collectors.toList())
                : reviewTaskRepository.findWithDetailsByStageAndCompetitionId(ReviewStage.FINAL, competitionId);

        if (tasks.isEmpty()) return new ArrayList<>();

        List<Long> taskIds = tasks.stream().map(ReviewTask::getId).collect(Collectors.toList());
        Map<Long, ReviewScore> scoreByTaskId = reviewScoreRepository.findByReviewTaskIdIn(taskIds)
                .stream().collect(Collectors.toMap(ReviewScore::getReviewTaskId, s -> s));

        return tasks.stream().map(t -> {
            Registration reg = t.getRegistration();
            ReviewScore score = scoreByTaskId.get(t.getId());
            UserAccount reviewer = t.getReviewer();
            return FinalTaskItem.builder()
                    .taskId(t.getId())
                    .registrationId(reg.getId())
                    .sessionCode(reg.getFinalSessionCode())
                    .sessionOrder(reg.getFinalSessionOrder())
                    .projectName(reg.getProjectName())
                    .institutionName(reg.getInstitution() != null ? reg.getInstitution().getName() : "")
                    .groupCode(reg.getGroupCode())
                    .scoreForm(reg.getFinalScoreForm())
                    .reviewerId(reviewer != null ? reviewer.getId() : null)
                    .reviewerName(reviewer != null ? reviewer.getName() : null)
                    .reviewerPhone(reviewer != null ? reviewer.getPhone() : null)
                    .status(t.getStatus().name())
                    .total(score != null ? score.getTotal() : null)
                    .scoreItems(buildScoreItems(score))
                    .draftScore(score != null ? toScoreRequest(score) : null)
                    .build();
        }).collect(Collectors.toList());
    }

    // ── 计算排名 ──────────────────────────────────────────────────────────────

    /**
     * 计算现场竞赛排名并持久化到 final_ranking_snapshots。
     * 每次调用先清空该竞赛旧快照，幂等可重复执行。
     *
     * 算法（以专场为单位）：
     *  1. 收集该专场所有已提交(SCORED)任务的 total 分 → 大分数池
     *  2. 池里分数 ≥ 3 个时，去掉最大值和最小值各一个
     *  3. 剩余分数按 registrationId 分组取均值 → trimmedAvg
     *  4. 按 trimmedAvg 降序排名（相同分并列，下一名跳过）
     */
    @Transactional
    public String computeRanking(Long competitionId) {
        // 清旧快照
        finalRankingSnapshotRepository.deleteByCompetitionId(competitionId);

        // 取所有专场
        List<String> sessionCodes = registrationRepository
                .findDistinctFinalSessionCodesByCompetitionId(competitionId);

        if (sessionCodes.isEmpty()) {
            return "无专场数据，请先导入专场分组";
        }

        LocalDateTime now = LocalDateTime.now();
        int totalSaved = 0;

        for (String sessionCode : sessionCodes) {
            // 该专场所有项目
            List<Registration> regs = registrationRepository
                    .findByCompetitionIdAndFinalSessionCode(competitionId, sessionCode);
            if (regs.isEmpty()) continue;

            Map<Long, Registration> regById = regs.stream()
                    .collect(Collectors.toMap(Registration::getId, r -> r));

            // 该专场所有已提交任务
            List<ReviewTask> tasks = reviewTaskRepository
                    .findWithDetailsByStageAndStatusAndCompetitionId(
                            ReviewStage.FINAL, ReviewStatus.SCORED, competitionId)
                    .stream()
                    .filter(t -> regById.containsKey(t.getRegistration().getId()))
                    .collect(Collectors.toList());

            if (tasks.isEmpty()) continue;

            List<Long> taskIds = tasks.stream().map(ReviewTask::getId).collect(Collectors.toList());
            Map<Long, ReviewScore> scoreByTaskId = reviewScoreRepository
                    .findByReviewTaskIdIn(taskIds).stream()
                    .collect(Collectors.toMap(ReviewScore::getReviewTaskId, s -> s));

            // 大分数池：所有 total 分（跳过无评分记录的任务）
            List<double[]> pool = new ArrayList<>(); // [registrationId, total]
            for (ReviewTask t : tasks) {
                ReviewScore s = scoreByTaskId.get(t.getId());
                if (s == null || s.getTotal() == null) continue;
                pool.add(new double[]{t.getRegistration().getId(), s.getTotal()});
            }

            if (pool.isEmpty()) continue;

            // 找极值
            Double removedMax = null;
            Double removedMin = null;
            boolean trimmed = pool.size() >= 3;
            List<double[]> effective = new ArrayList<>(pool);

            if (trimmed) {
                double maxVal = pool.stream().mapToDouble(a -> a[1]).max().getAsDouble();
                double minVal = pool.stream().mapToDouble(a -> a[1]).min().getAsDouble();
                removedMax = maxVal;
                removedMin = minVal;
                // 各去掉一个（只去一次，用标志位）
                boolean maxRemoved = false, minRemoved = false;
                List<double[]> filtered = new ArrayList<>();
                for (double[] entry : pool) {
                    if (!maxRemoved && entry[1] == maxVal) { maxRemoved = true; continue; }
                    if (!minRemoved && entry[1] == minVal) { minRemoved = true; continue; }
                    filtered.add(entry);
                }
                effective = filtered;
            }

            // 按 registrationId 分组取均值
            Map<Long, List<Double>> scoresByReg = new java.util.LinkedHashMap<>();
            for (double[] e : effective) {
                scoresByReg.computeIfAbsent((long) e[0], k -> new ArrayList<>()).add(e[1]);
            }

            // 构建快照（先不排名）
            List<FinalRankingSnapshot> snapshots = new ArrayList<>();
            for (Registration reg : regs) {
                List<Double> regScores = scoresByReg.get(reg.getId());
                double trimmedAvg = 0.0;
                int cnt = 0;
                if (regScores != null && !regScores.isEmpty()) {
                    trimmedAvg = regScores.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
                    cnt = regScores.size();
                }
                snapshots.add(FinalRankingSnapshot.builder()
                        .competitionId(competitionId)
                        .registrationId(reg.getId())
                        .sessionDate(reg.getFinalSessionDate())
                        .sessionCode(sessionCode)
                        .sessionOrder(reg.getFinalSessionOrder())
                        .scoreForm(reg.getFinalScoreForm())
                        .judgeScoreCount(cnt)
                        .sessionRemovedMax(removedMax)
                        .sessionRemovedMin(removedMin)
                        .trimmedAvg(trimmedAvg)
                        .calculatedAt(now)
                        .build());
            }

            // 按 trimmedAvg 降序排名（并列相同名次，下一名跳过）
            snapshots.sort((a, b) -> Double.compare(b.getTrimmedAvg(), a.getTrimmedAvg()));
            int rank = 1;
            for (int i = 0; i < snapshots.size(); i++) {
                if (i > 0 && !snapshots.get(i).getTrimmedAvg().equals(snapshots.get(i - 1).getTrimmedAvg())) {
                    rank = i + 1;
                }
                snapshots.get(i).setSessionRank(rank);
            }

            finalRankingSnapshotRepository.saveAll(snapshots);
            totalSaved += snapshots.size();
        }

        return String.format("排名计算完成，共处理 %d 个专场，写入 %d 条记录", sessionCodes.size(), totalSaved);
    }

    // ── 查询排名 ──────────────────────────────────────────────────────────────

    public List<FinalRankingItem> getRanking(Long competitionId, String sessionCode) {
        List<FinalRankingSnapshot> snapshots = sessionCode != null
                ? finalRankingSnapshotRepository
                        .findByCompetitionIdAndSessionCodeOrderBySessionRankAsc(competitionId, sessionCode)
                : finalRankingSnapshotRepository
                        .findByCompetitionIdOrderBySessionCodeAscSessionRankAsc(competitionId);

        // 取 registration 信息（项目名称、机构）
        List<Long> regIds = snapshots.stream().map(FinalRankingSnapshot::getRegistrationId)
                .collect(Collectors.toList());
        Map<Long, Registration> regMap = registrationRepository.findByIdInWithInstitution(regIds)
                .stream().collect(Collectors.toMap(Registration::getId, r -> r));

        return snapshots.stream().map(s -> {
            Registration reg = regMap.get(s.getRegistrationId());
            return FinalRankingItem.builder()
                    .sessionDate(s.getSessionDate())
                    .sessionCode(s.getSessionCode())
                    .rank(s.getSessionRank())
                    .registrationId(s.getRegistrationId())
                    .sessionOrder(s.getSessionOrder())
                    .projectName(reg != null ? reg.getProjectName() : "")
                    .institutionName(reg != null && reg.getInstitution() != null
                            ? reg.getInstitution().getName() : "")
                    .scoreForm(s.getScoreForm())
                    .judgeCount(s.getJudgeScoreCount() != null ? s.getJudgeScoreCount() : 0)
                    .trimmedAvg(s.getTrimmedAvg())
                    .note(s.getSessionRemovedMax() == null
                            ? "分数不足3个，未去极值"
                            : String.format("去掉最高%.1f、最低%.1f", s.getSessionRemovedMax(), s.getSessionRemovedMin()))
                    .build();
        }).collect(Collectors.toList());
    }

    // ── 全局混合排名 ──────────────────────────────────────────────────────────

    /**
     * 把所有专场的项目汇总到一起，按 trimmedAvg 降序统一排名。
     * 依赖已存在的 final_ranking_snapshots 数据（需先执行 compute-ranking）。
     */
    public List<FinalRankingItem> getMixedRanking(Long competitionId) {
        List<FinalRankingSnapshot> all = finalRankingSnapshotRepository
                .findByCompetitionIdOrderBySessionCodeAscSessionRankAsc(competitionId);

        if (all.isEmpty()) return new ArrayList<>();

        // 统一按 trimmedAvg 降序排
        all.sort((a, b) -> Double.compare(
                b.getTrimmedAvg() != null ? b.getTrimmedAvg() : 0.0,
                a.getTrimmedAvg() != null ? a.getTrimmedAvg() : 0.0));

        List<Long> regIds = all.stream().map(FinalRankingSnapshot::getRegistrationId)
                .collect(Collectors.toList());
        Map<Long, Registration> regMap = registrationRepository.findByIdInWithInstitution(regIds)
                .stream().collect(Collectors.toMap(Registration::getId, r -> r));

        List<FinalRankingItem> result = new ArrayList<>();
        int rank = 1;
        for (int i = 0; i < all.size(); i++) {
            FinalRankingSnapshot s = all.get(i);
            if (i > 0) {
                Double prev = all.get(i - 1).getTrimmedAvg();
                Double curr = s.getTrimmedAvg();
                boolean same = (prev == null && curr == null)
                        || (prev != null && prev.equals(curr));
                if (!same) rank = i + 1;
            }
            Registration reg = regMap.get(s.getRegistrationId());
            result.add(FinalRankingItem.builder()
                    .sessionDate(s.getSessionDate())
                    .sessionCode(s.getSessionCode())
                    .rank(rank)
                    .registrationId(s.getRegistrationId())
                    .sessionOrder(s.getSessionOrder())
                    .projectName(reg != null ? reg.getProjectName() : "")
                    .institutionName(reg != null && reg.getInstitution() != null
                            ? reg.getInstitution().getName() : "")
                    .scoreForm(s.getScoreForm())
                    .judgeCount(s.getJudgeScoreCount() != null ? s.getJudgeScoreCount() : 0)
                    .trimmedAvg(s.getTrimmedAvg())
                    .note(s.getSessionRemovedMax() == null
                            ? "分数不足3个，未去极值"
                            : String.format("去掉最高%.1f、最低%.1f",
                                    s.getSessionRemovedMax(), s.getSessionRemovedMin()))
                    .build());
        }
        return result;
    }

    // ── 导出排名 Excel ────────────────────────────────────────────────────────

    public byte[] exportRankingExcel(Long competitionId, String sessionCode) throws Exception {
        List<FinalRankingItem> items = getRanking(competitionId, sessionCode);

        try (Workbook wb = new XSSFWorkbook()) {
            // 样式
            CellStyle headerStyle = wb.createCellStyle();
            Font headerFont = wb.createFont();
            headerFont.setBold(true);
            headerStyle.setFont(headerFont);
            headerStyle.setFillForegroundColor(IndexedColors.GREY_25_PERCENT.getIndex());
            headerStyle.setFillPattern(FillPatternType.SOLID_FOREGROUND);

            // 按专场分 Sheet
            java.util.Map<String, List<FinalRankingItem>> bySession = new java.util.LinkedHashMap<>();
            for (FinalRankingItem item : items) {
                bySession.computeIfAbsent(item.getSessionCode(), k -> new ArrayList<>()).add(item);
            }

            // 若只有一个专场，直接用专场名命名 sheet；否则每个专场一个 sheet + 一个汇总 sheet
            boolean multiSession = bySession.size() > 1;

            if (multiSession) {
                // 汇总 sheet（全部专场合在一起）
                Sheet summary = wb.createSheet("全部专场");
                writeRankingSheet(summary, items, headerStyle, true);
            }

            for (Map.Entry<String, List<FinalRankingItem>> entry : bySession.entrySet()) {
                // sheet 名最多 31 字符
                String sheetName = entry.getKey().length() > 31
                        ? entry.getKey().substring(0, 31) : entry.getKey();
                Sheet sheet = wb.createSheet(sheetName);
                writeRankingSheet(sheet, entry.getValue(), headerStyle, false);
            }

            java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
            wb.write(out);
            return out.toByteArray();
        }
    }

    private void writeRankingSheet(Sheet sheet, List<FinalRankingItem> items,
                                   CellStyle headerStyle, boolean includeSessionCol) {
        // 列头
        String[] headers = includeSessionCol
                ? new String[]{"专场", "排名", "上台顺序", "项目名称", "机构名称", "评分表", "参与评委数", "去极值均分", "备注"}
                : new String[]{"排名", "上台顺序", "项目名称", "机构名称", "评分表", "参与评委数", "去极值均分", "备注"};

        Row hRow = sheet.createRow(0);
        for (int i = 0; i < headers.length; i++) {
            Cell c = hRow.createCell(i);
            c.setCellValue(headers[i]);
            c.setCellStyle(headerStyle);
            sheet.setColumnWidth(i, 5000);
        }
        sheet.setColumnWidth(includeSessionCol ? 3 : 2, 14000); // 项目名称列宽
        sheet.setColumnWidth(includeSessionCol ? 4 : 3, 10000); // 机构名称列宽
        sheet.setColumnWidth(includeSessionCol ? 8 : 7, 10000); // 备注列宽

        int rowNum = 1;
        for (FinalRankingItem item : items) {
            Row row = sheet.createRow(rowNum++);
            int col = 0;
            if (includeSessionCol) row.createCell(col++).setCellValue(item.getSessionCode());
            row.createCell(col++).setCellValue(item.getRank());
            row.createCell(col++).setCellValue(item.getSessionOrder() != null ? item.getSessionOrder() : 0);
            row.createCell(col++).setCellValue(item.getProjectName());
            row.createCell(col++).setCellValue(item.getInstitutionName());
            row.createCell(col++).setCellValue(item.getScoreForm());
            row.createCell(col++).setCellValue(item.getJudgeCount());
            Cell avgCell = row.createCell(col++);
            if (item.getTrimmedAvg() != null) avgCell.setCellValue(item.getTrimmedAvg());
            row.createCell(col).setCellValue(item.getNote() != null ? item.getNote() : "");
        }
    }

    // ── 内部工具方法 ──────────────────────────────────────────────────────────

    private double computeTotal(FinalScoreRequest r) {
        double sum = 0;
        if (r.getPlan() != null) sum += r.getPlan();
        if (r.getProblem() != null) sum += r.getProblem();
        if (r.getAction() != null) sum += r.getAction();
        if (r.getSuccess() != null) sum += r.getSuccess();
        if (r.getReview() != null) sum += r.getReview();
        if (r.getOperation() != null) sum += r.getOperation();
        if (r.getPresentation() != null) sum += r.getPresentation();
        if (r.getItem8() != null) sum += r.getItem8();
        return sum;
    }

    private FinalScoreRequest toScoreRequest(ReviewScore s) {
        FinalScoreRequest r = new FinalScoreRequest();
        r.setScoreForm(s.getScoreForm());
        r.setPlan(s.getPlan());
        r.setProblem(s.getProblem());
        r.setAction(s.getAction());
        r.setSuccess(s.getSuccess());
        r.setReview(s.getReview());
        r.setOperation(s.getOperation());
        r.setPresentation(s.getPresentation());
        r.setItem8(s.getItem8());
        r.setTotal(s.getTotal());
        r.setHighlight(s.getHighlight());
        r.setWeakness(s.getWeakness());
        return r;
    }

    private String normalizeScoreForm(String raw) {
        if (raw == null) return null;
        switch (raw.trim()) {
            case "QCC": return "QCC";
            case "QFD": return "QFD";
            case "非QCC": return "NON_QCC";
            default: return raw.trim();
        }
    }

    private String extractSessionCodeFromSheetName(String sheetName) {
        // 去掉日期前缀（6.3/6.4/6.5）和括号内容
        return sheetName.replaceAll("^\\d+\\.\\d+", "").replaceAll("（.*?）", "").replaceAll("\\(.*?\\)", "").trim();
    }

    private Long getCellLong(Row row, int col) {
        Cell c = row.getCell(col);
        if (c == null) return null;
        try {
            if (c.getCellType() == CellType.NUMERIC) return (long) c.getNumericCellValue();
            String s = c.toString().trim();
            return s.isEmpty() ? null : Long.parseLong(s);
        } catch (Exception e) {
            return null;
        }
    }

    private Integer getCellInt(Row row, int col) {
        Cell c = row.getCell(col);
        if (c == null) return null;
        try {
            if (c.getCellType() == CellType.NUMERIC) return (int) c.getNumericCellValue();
            String s = c.toString().trim();
            return s.isEmpty() ? null : Integer.parseInt(s);
        } catch (Exception e) {
            return null;
        }
    }

    private String getCellString(Row row, int col) {
        Cell c = row.getCell(col);
        if (c == null) return null;
        if (c.getCellType() == CellType.NUMERIC) return String.valueOf((long) c.getNumericCellValue());
        String v = c.toString().trim();
        return v.isEmpty() ? null : v;
    }

    /**
     * 将 ReviewScore 的原始字段按 scoreForm 翻译为带标签的分项列表。
     * 前端可直接渲染，无需自行映射字段名。
     */
    private List<FinalScoreItem> buildScoreItems(ReviewScore s) {
        if (s == null) return null;
        String sf = s.getScoreForm();
        List<FinalScoreItem> items = new ArrayList<>();
        if ("QCC".equals(sf)) {
            items.add(new FinalScoreItem("计划",    10, s.getPlan()));
            items.add(new FinalScoreItem("项目结构", 15, s.getProblem()));
            items.add(new FinalScoreItem("对策行动", 15, s.getAction()));
            items.add(new FinalScoreItem("成果表现", 20, s.getSuccess()));
            items.add(new FinalScoreItem("查验",      5, s.getReview()));
            items.add(new FinalScoreItem("整体运作", 15, s.getOperation()));
            items.add(new FinalScoreItem("现场表现", 20, s.getPresentation()));
        } else if ("QFD".equals(sf)) {
            items.add(new FinalScoreItem("圈活动特征",             10, s.getPlan()));
            items.add(new FinalScoreItem("质量规划与课题明确化",   30, s.getProblem()));
            items.add(new FinalScoreItem("质量设计与方策拟定",     35, s.getAction()));
            items.add(new FinalScoreItem("执行力及活动成果",       20, s.getSuccess()));
            items.add(new FinalScoreItem("现场发表",                5, s.getReview()));
        } else if ("NON_QCC".equals(sf)) {
            items.add(new FinalScoreItem("选题",    15, s.getPlan()));
            items.add(new FinalScoreItem("原因分析", 10, s.getProblem()));
            items.add(new FinalScoreItem("计划",    10, s.getAction()));
            items.add(new FinalScoreItem("实施",    20, s.getSuccess()));
            items.add(new FinalScoreItem("成果表现", 10, s.getReview()));
            items.add(new FinalScoreItem("检讨",    10, s.getOperation()));
            items.add(new FinalScoreItem("整体运作", 15, s.getPresentation()));
            items.add(new FinalScoreItem("现场表现", 10, s.getItem8()));
        }
        return items;
    }

    private <T extends Comparable<T>> int compareNullable(T a, T b) {
        if (a == null && b == null) return 0;
        if (a == null) return 1;
        if (b == null) return -1;
        return a.compareTo(b);
    }

    /**
     * 全局场次对应表：三天 × 21场次 × 各场项目列表，一次返回。
     * 结果按 sessionDate asc、sessionCode asc 排序。
     */
    public List<FinalScheduleSession> getSessionSchedule(Long competitionId) {
        List<Object[]> rows = registrationRepository
                .findDistinctFinalSessionsByCompetitionId(competitionId);
        List<FinalScheduleSession> result = new ArrayList<>();
        for (Object[] row : rows) {
            String date = (String) row[0];
            String code = (String) row[1];
            List<FinalProjectItem> projects = listProjectsBySession(competitionId, code);
            int qcc = 0, qfd = 0, nonQcc = 0;
            for (FinalProjectItem p : projects) {
                if ("QCC".equals(p.getScoreForm())) qcc++;
                else if ("QFD".equals(p.getScoreForm())) qfd++;
                else if ("NON_QCC".equals(p.getScoreForm())) nonQcc++;
            }
            result.add(new FinalScheduleSession(date, code, projects.size(), qcc, qfd, nonQcc, projects));
        }
        return result;
    }
}
