package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.ScoringSnapshot;
import com.trae.pinguan.domain.entity.SystemSetting;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ShortlistOverride;
import com.trae.pinguan.repository.RegistrationRepository;
import com.trae.pinguan.repository.ScoringSnapshotRepository;
import com.trae.pinguan.repository.SystemSettingRepository;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.AdvancedRankingConfigRequest;
import com.trae.pinguan.web.dto.BookScopeConfigRequest;
import com.trae.pinguan.web.dto.ShortlistConfigRequest;
import com.trae.pinguan.web.dto.ShortlistItem;
import com.trae.pinguan.web.dto.ShortlistOverrideRequest;
import com.trae.pinguan.web.dto.ShortlistResult;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.Collections;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin/shortlist")
@RequiredArgsConstructor
@Tag(name = "入围管理")
@SecurityRequirement(name = "BearerAuth")
public class AdminShortlistController {

    private final ScoringSnapshotRepository snapshotRepository;
    private final RegistrationRepository registrationRepository;
    private final SystemSettingRepository systemSettingRepository;

    // ─── 入围配置（各组独立） ────────────────────────────────────

    @GetMapping("/config")
    @Operation(summary = "查询各组别入围配置（BASIC/COMPREHENSIVE/ADVANCED）")
    public ApiResponse<List<Map<String, Object>>> getConfig() {
        List<Map<String, Object>> result = new ArrayList<>();
        for (GroupType gt : GroupType.values()) {
            Map<String, Object> item = new HashMap<>();
            item.put("groupType", gt.name());
            item.put("mode",  settingVal(shortlistModeKey(gt),  "RATIO"));
            item.put("value", Double.parseDouble(settingVal(shortlistValueKey(gt), "0.55")));
            result.add(item);
        }
        return ApiResponse.ok(result);
    }

    @PutMapping("/config")
    @Operation(summary = "保存某个组别的入围配置（书审阶段用 BASIC/COMPREHENSIVE，面谈阶段用 ADVANCED）")
    @Transactional
    public ApiResponse<Void> saveConfig(@Valid @RequestBody ShortlistConfigRequest req) {
        upsertSetting(shortlistModeKey(req.getGroupType()), req.getMode());
        upsertSetting(shortlistValueKey(req.getGroupType()), String.valueOf(req.getValue()));
        return ApiResponse.ok(null);
    }

    // ─── 书审阶段入围范围配置（PER_GROUP / UNIFIED） ─────────────

    @GetMapping("/book-scope")
    @Operation(summary = "查询书审阶段入围范围配置",
               description = "PER_GROUP=基层组+综合组各自独立入围；UNIFIED=两组合并统一比例/取前N名入围")
    public ApiResponse<Map<String, Object>> getBookScope() {
        Map<String, Object> cfg = new HashMap<>();
        cfg.put("scope",        settingVal("shortlist_BOOK_scope",         "PER_GROUP"));
        cfg.put("unifiedMode",  settingVal("shortlist_BOOK_unified_mode",  "RATIO"));
        cfg.put("unifiedValue", Double.parseDouble(settingVal("shortlist_BOOK_unified_value", "0.55")));
        return ApiResponse.ok(cfg);
    }

    @PutMapping("/book-scope")
    @Operation(summary = "保存书审阶段入围范围配置")
    @Transactional
    public ApiResponse<Void> saveBookScope(@Valid @RequestBody BookScopeConfigRequest req) {
        upsertSetting("shortlist_BOOK_scope", req.getScope());
        if (req.getUnifiedMode()  != null) upsertSetting("shortlist_BOOK_unified_mode",  req.getUnifiedMode());
        if (req.getUnifiedValue() != null) upsertSetting("shortlist_BOOK_unified_value", String.valueOf(req.getUnifiedValue()));
        return ApiResponse.ok(null);
    }

    // ─── 入围名单查询 ────────────────────────────────────────────

    @GetMapping
    @Operation(summary = "查询入围名单",
               description = "书审阶段(BOOK)只返回基层组+综合组；面谈阶段(INTERVIEW)只返回进阶组。" +
                             "返回体中含本次计算的配置摘要（scope/mode/value/cutoff 及各组配置）。")
    @Transactional(readOnly = true)
    public ApiResponse<ShortlistResult> list(
            @RequestParam Long competitionId,
            @RequestParam ReviewStage stage,
            @RequestParam(required = false) GroupType groupType) {

        // ── 根据阶段确定参与入围的组别 ──
        List<ScoringSnapshot> snapshots;
        if (groupType != null) {
            snapshots = snapshotRepository.findByCompetitionIdAndStageAndGroupTypeOrderByIrankAsc(
                    competitionId, stage, groupType);
        } else if (stage == ReviewStage.BOOK) {
            List<ScoringSnapshot> basic = snapshotRepository
                    .findByCompetitionIdAndStageAndGroupTypeOrderByIrankAsc(competitionId, stage, GroupType.BASIC);
            List<ScoringSnapshot> comp  = snapshotRepository
                    .findByCompetitionIdAndStageAndGroupTypeOrderByIrankAsc(competitionId, stage, GroupType.COMPREHENSIVE);
            snapshots = new ArrayList<>();
            snapshots.addAll(basic);
            snapshots.addAll(comp);
        } else if (stage == ReviewStage.INTERVIEW) {
            snapshots = snapshotRepository.findByCompetitionIdAndStageAndGroupTypeOrderByIrankAsc(
                    competitionId, stage, GroupType.ADVANCED);
        } else {
            snapshots = snapshotRepository.findByCompetitionIdAndStageOrderByIrankAsc(competitionId, stage);
        }

        if (snapshots.isEmpty()) {
            return ApiResponse.ok(ShortlistResult.builder()
                    .stage(stage.name())
                    .totalCount(0).shortlistCount(0).shortlistRatio(0)
                    .items(new ArrayList<>())
                    .build());
        }

        Set<Long> regIds = snapshots.stream()
                .map(ScoringSnapshot::getRegistrationId).collect(Collectors.toSet());
        Map<Long, Registration> regMap = registrationRepository.findAllById(regIds).stream()
                .collect(Collectors.toMap(Registration::getId, r -> r));

        // ── 计算每个快照是否在入围线内 ──
        Map<Long, Boolean> withinLineMap = computeWithinLine(snapshots, stage, groupType);

        List<ShortlistItem> items = new ArrayList<>();
        for (ScoringSnapshot s : snapshots) {
            Registration reg = regMap.get(s.getRegistrationId());
            boolean withinLine = withinLineMap.getOrDefault(s.getRegistrationId(), false);
            ShortlistOverride override = reg != null ? reg.getShortlistOverride() : null;
            boolean shortlisted;
            if (override == ShortlistOverride.INCLUDE)       shortlisted = true;
            else if (override == ShortlistOverride.EXCLUDE)  shortlisted = false;
            else                                              shortlisted = withinLine;

            items.add(ShortlistItem.builder()
                    .irank(s.getIrank())
                    .registrationId(s.getRegistrationId())
                    .projectName(reg != null ? reg.getProjectName() : null)
                    .institutionName(reg != null && reg.getInstitution() != null
                            ? reg.getInstitution().getName() : null)
                    .groupType(s.getGroupType())
                    .groupCode(s.getGroupCode())
                    .stage(s.getStage())
                    .rawAvg(s.getRawAvg())
                    .groupAvg(s.getGroupAvg())
                    .overallAvg(s.getOverallAvg())
                    .coefficient(s.getCoefficient())
                    .adjustedScore(s.getAdjustedScore())
                    .calculatedAt(s.getCalculatedAt())
                    .withinLine(withinLine)
                    .shortlisted(shortlisted)
                    .shortlistOverride(override)
                    .shortlistNote(reg != null ? reg.getShortlistNote() : null)
                    .build());
        }

        // ── 最近快照时间 ──
        java.time.LocalDateTime snapshotAt = snapshots.stream()
                .map(ScoringSnapshot::getCalculatedAt)
                .filter(t -> t != null)
                .max(java.util.Comparator.naturalOrder())
                .orElse(null);

        int shortlistCount = (int) items.stream().filter(ShortlistItem::getShortlisted).count();
        int totalCount     = items.size();
        double ratio       = totalCount > 0 ? (double) shortlistCount / totalCount : 0;

        // ── 构建配置摘要 ──
        ShortlistResult.ShortlistResultBuilder builder = ShortlistResult.builder()
                .stage(stage.name())
                .snapshotAt(snapshotAt)
                .totalCount(totalCount)
                .shortlistCount(shortlistCount)
                .shortlistRatio(Math.round(ratio * 1000.0) / 1000.0);

        boolean isUnified = stage == ReviewStage.BOOK && groupType == null
                && "UNIFIED".equalsIgnoreCase(settingVal("shortlist_BOOK_scope", "PER_GROUP"));

        if (stage == ReviewStage.BOOK && groupType == null) {
            String scope = settingVal("shortlist_BOOK_scope", "PER_GROUP");
            builder.scope(scope);

            if (isUnified) {
                String uMode  = settingVal("shortlist_BOOK_unified_mode", "RATIO");
                double uValue = Double.parseDouble(settingVal("shortlist_BOOK_unified_value", "0.55"));
                int uCutoff   = "COUNT".equalsIgnoreCase(uMode)
                        ? (int) Math.min(uValue, totalCount)
                        : (int) Math.round(totalCount * uValue);
                builder.unifiedMode(uMode).unifiedValue(uValue).unifiedCutoff(uCutoff);
                // UNIFIED：按调整分重新排序输出
                items.sort((a, b) -> {
                    double da = a.getAdjustedScore() != null ? a.getAdjustedScore() : 0;
                    double db = b.getAdjustedScore() != null ? b.getAdjustedScore() : 0;
                    return Double.compare(db, da);
                });
            } else {
                // PER_GROUP：汇总每组配置
                List<Map<String, Object>> groupConfigs = new ArrayList<>();
                Map<GroupType, List<ShortlistItem>> byGt = items.stream()
                        .collect(Collectors.groupingBy(ShortlistItem::getGroupType));
                for (Map.Entry<GroupType, List<ShortlistItem>> e : byGt.entrySet()) {
                    GroupType gt   = e.getKey();
                    List<ShortlistItem> gItems = e.getValue();
                    int gTotal     = gItems.size();
                    int gCutoff    = computePerGroupCutoff(gt, gTotal);
                    int gWithin    = (int) gItems.stream().filter(ShortlistItem::getWithinLine).count();
                    String gMode   = settingVal(shortlistModeKey(gt), "RATIO");
                    double gValue  = Double.parseDouble(settingVal(shortlistValueKey(gt), "0.55"));
                    Map<String, Object> gcfg = new HashMap<>();
                    gcfg.put("groupType",       gt.name());
                    gcfg.put("mode",            gMode);
                    gcfg.put("value",           gValue);
                    gcfg.put("cutoff",          gCutoff);
                    gcfg.put("total",           gTotal);
                    gcfg.put("withinLineCount", gWithin);
                    groupConfigs.add(gcfg);
                }
                builder.groupConfigs(groupConfigs);
            }
        } else if (stage == ReviewStage.INTERVIEW) {
            // 面谈阶段：只有进阶组，展示其配置
            GroupType gt   = GroupType.ADVANCED;
            int gTotal     = totalCount;
            int gCutoff    = computePerGroupCutoff(gt, gTotal);
            int gWithin    = (int) items.stream().filter(ShortlistItem::getWithinLine).count();
            String gMode   = settingVal(shortlistModeKey(gt), "RATIO");
            double gValue  = Double.parseDouble(settingVal(shortlistValueKey(gt), "0.55"));
            Map<String, Object> gcfg = new HashMap<>();
            gcfg.put("groupType",       gt.name());
            gcfg.put("mode",            gMode);
            gcfg.put("value",           gValue);
            gcfg.put("cutoff",          gCutoff);
            gcfg.put("total",           gTotal);
            gcfg.put("withinLineCount", gWithin);
            builder.groupConfigs(Collections.singletonList(gcfg));
        }

        return ApiResponse.ok(builder.items(items).build());
    }

    // ─── 人工干预 ────────────────────────────────────────────────

    @PutMapping("/override")
    @Operation(summary = "设置人工干预（强制入围 / 强制淘汰）")
    @Transactional
    public ApiResponse<Void> setOverride(@Valid @RequestBody ShortlistOverrideRequest req) {
        Registration reg = registrationRepository.findById(req.getRegistrationId())
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        reg.setShortlistOverride(req.getOverride());
        reg.setShortlistNote(req.getNote());
        registrationRepository.save(reg);
        return ApiResponse.ok(null);
    }

    @DeleteMapping("/override/{registrationId}")
    @Operation(summary = "撤销人工干预")
    @Transactional
    public ApiResponse<Void> clearOverride(@PathVariable Long registrationId) {
        Registration reg = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("报名不存在"));
        reg.setShortlistOverride(null);
        reg.setShortlistNote(null);
        registrationRepository.save(reg);
        return ApiResponse.ok(null);
    }

    // ─── 私有工具方法 ────────────────────────────────────────────

    /**
     * 计算每个快照是否在入围线内，支持 PER_GROUP 和 UNIFIED 两种书审模式。
     */
    private Map<Long, Boolean> computeWithinLine(List<ScoringSnapshot> snapshots,
                                                  ReviewStage stage, GroupType explicitGroupType) {
        Map<Long, Boolean> result = new HashMap<>();

        boolean isUnified = stage == ReviewStage.BOOK
                && explicitGroupType == null
                && "UNIFIED".equalsIgnoreCase(settingVal("shortlist_BOOK_scope", "PER_GROUP"));

        if (isUnified) {
            // UNIFIED：合并所有快照，按调整分排序，取前 N / 前 X%
            String mode = settingVal("shortlist_BOOK_unified_mode", "RATIO");
            double val  = Double.parseDouble(settingVal("shortlist_BOOK_unified_value", "0.55"));
            int total   = snapshots.size();
            int cutoff  = "COUNT".equalsIgnoreCase(mode)
                    ? (int) Math.min(val, total)
                    : (int) Math.round(total * val);

            // 按调整分降序赋临时排名
            List<ScoringSnapshot> sorted = snapshots.stream()
                    .sorted((a, b) -> {
                        double da = a.getAdjustedScore() != null ? a.getAdjustedScore() : 0;
                        double db = b.getAdjustedScore() != null ? b.getAdjustedScore() : 0;
                        return Double.compare(db, da);
                    })
                    .collect(Collectors.toList());
            for (int i = 0; i < sorted.size(); i++) {
                result.put(sorted.get(i).getRegistrationId(), (i + 1) <= cutoff);
            }
        } else {
            // PER_GROUP：每个 groupType 独立计算入围线
            Map<GroupType, List<ScoringSnapshot>> byGt = snapshots.stream()
                    .collect(Collectors.groupingBy(ScoringSnapshot::getGroupType));
            for (Map.Entry<GroupType, List<ScoringSnapshot>> entry : byGt.entrySet()) {
                GroupType gt    = entry.getKey();
                int total       = entry.getValue().size();
                int cutoff      = computePerGroupCutoff(gt, total);
                for (ScoringSnapshot s : entry.getValue()) {
                    result.put(s.getRegistrationId(),
                            s.getIrank() != null && s.getIrank() <= cutoff);
                }
            }
        }
        return result;
    }

    private int computePerGroupCutoff(GroupType groupType, int totalCount) {
        String mode = settingVal(shortlistModeKey(groupType), "RATIO");
        double v    = Double.parseDouble(settingVal(shortlistValueKey(groupType), "0.55"));
        if ("COUNT".equalsIgnoreCase(mode)) {
            return (int) Math.min(v, totalCount);
        }
        return (int) Math.round(totalCount * v);
    }

    private String shortlistModeKey(GroupType gt) {
        return "shortlist_" + gt.name() + "_mode";
    }

    private String shortlistValueKey(GroupType gt) {
        return "shortlist_" + gt.name() + "_value";
    }

    // ─── 进阶组合分配置 ──────────────────────────────────────────

    @GetMapping("/advanced-ranking-config")
    @Operation(summary = "查询进阶组合分配置（书审/面谈权重 + 调整模式）")
    public ApiResponse<Map<String, Object>> getAdvancedConfig() {
        Map<String, Object> cfg = new HashMap<>();
        cfg.put("bookWeight",     Double.parseDouble(settingVal("advanced_book_weight",     "0.4")));
        cfg.put("interviewWeight",Double.parseDouble(settingVal("advanced_interview_weight","0.6")));
        cfg.put("rankingMode",    settingVal("advanced_ranking_mode", "ADJUST_THEN_WEIGHT"));
        return ApiResponse.ok(cfg);
    }

    @PutMapping("/advanced-ranking-config")
    @Operation(summary = "保存进阶组合分配置")
    @Transactional
    public ApiResponse<Void> saveAdvancedConfig(@Valid @RequestBody AdvancedRankingConfigRequest req) {
        upsertSetting("advanced_book_weight",      String.valueOf(req.getBookWeight()));
        upsertSetting("advanced_interview_weight", String.valueOf(req.getInterviewWeight()));
        upsertSetting("advanced_ranking_mode",     req.getRankingMode());
        return ApiResponse.ok(null);
    }

    private String settingVal(String key, String defaultVal) {
        return systemSettingRepository.findBySettingKey(key)
                .map(SystemSetting::getSettingValue).orElse(defaultVal);
    }

    private void upsertSetting(String key, String value) {
        SystemSetting s = systemSettingRepository.findBySettingKey(key)
                .orElse(SystemSetting.builder().settingKey(key).build());
        s.setSettingValue(value);
        s.setUpdatedAt(LocalDateTime.now());
        systemSettingRepository.save(s);
    }
}
