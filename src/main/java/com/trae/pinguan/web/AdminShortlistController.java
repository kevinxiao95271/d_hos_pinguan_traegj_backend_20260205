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
import com.trae.pinguan.web.dto.ShortlistConfigRequest;
import com.trae.pinguan.web.dto.ShortlistItem;
import com.trae.pinguan.web.dto.ShortlistOverrideRequest;
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

    // ─── 入围配置 ───────────────────────────────────────────────

    @GetMapping("/config")
    @Operation(summary = "查询入围配置（三个组别）")
    public ApiResponse<List<Map<String, Object>>> getConfig() {
        List<Map<String, Object>> result = new ArrayList<>();
        for (GroupType gt : GroupType.values()) {
            String modeKey = shortlistModeKey(gt);
            String valKey = shortlistValueKey(gt);
            String mode = systemSettingRepository.findBySettingKey(modeKey)
                    .map(SystemSetting::getSettingValue).orElse("RATIO");
            String val = systemSettingRepository.findBySettingKey(valKey)
                    .map(SystemSetting::getSettingValue).orElse("0.55");
            Map<String, Object> item = new HashMap<>();
            item.put("groupType", gt.name());
            item.put("mode", mode);
            item.put("value", Double.parseDouble(val));
            result.add(item);
        }
        return ApiResponse.ok(result);
    }

    @PutMapping("/config")
    @Operation(summary = "保存入围配置")
    @Transactional
    public ApiResponse<Void> saveConfig(@Valid @RequestBody ShortlistConfigRequest req) {
        upsertSetting(shortlistModeKey(req.getGroupType()), req.getMode());
        upsertSetting(shortlistValueKey(req.getGroupType()), String.valueOf(req.getValue()));
        return ApiResponse.ok(null);
    }

    // ─── 入围名单查询 ────────────────────────────────────────────

    @GetMapping
    @Operation(summary = "查询入围名单（含入围线、人工干预标注）")
    @Transactional(readOnly = true)
    public ApiResponse<List<ShortlistItem>> list(
            @RequestParam Long competitionId,
            @RequestParam ReviewStage stage,
            @RequestParam(required = false) GroupType groupType) {

        List<ScoringSnapshot> snapshots = groupType != null
                ? snapshotRepository.findByCompetitionIdAndStageAndGroupTypeOrderByIrankAsc(
                        competitionId, stage, groupType)
                : snapshotRepository.findByCompetitionIdAndStageOrderByIrankAsc(competitionId, stage);

        if (snapshots.isEmpty()) {
            return ApiResponse.ok(new ArrayList<>());
        }

        Set<Long> regIds = snapshots.stream()
                .map(ScoringSnapshot::getRegistrationId)
                .collect(Collectors.toSet());
        Map<Long, Registration> regMap = registrationRepository.findAllById(regIds).stream()
                .collect(Collectors.toMap(Registration::getId, r -> r));

        List<ShortlistItem> items = new ArrayList<>();

        // 按 groupType 分组计算入围线
        Map<GroupType, Integer> cutoffMap = new HashMap<>();
        Map<GroupType, List<ScoringSnapshot>> byGroupType = snapshots.stream()
                .collect(Collectors.groupingBy(ScoringSnapshot::getGroupType));
        for (Map.Entry<GroupType, List<ScoringSnapshot>> entry : byGroupType.entrySet()) {
            GroupType gt = entry.getKey();
            int total = entry.getValue().size();
            cutoffMap.put(gt, computeCutoff(gt, total));
        }

        for (ScoringSnapshot s : snapshots) {
            Registration reg = regMap.get(s.getRegistrationId());
            int cutoff = cutoffMap.getOrDefault(s.getGroupType(), total(s.getGroupType(), snapshots));
            boolean withinLine = s.getIrank() != null && s.getIrank() <= cutoff;

            ShortlistOverride override = reg != null ? reg.getShortlistOverride() : null;
            boolean shortlisted;
            if (override == ShortlistOverride.INCLUDE) {
                shortlisted = true;
            } else if (override == ShortlistOverride.EXCLUDE) {
                shortlisted = false;
            } else {
                shortlisted = withinLine;
            }

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
        return ApiResponse.ok(items);
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

    private int computeCutoff(GroupType groupType, int totalCount) {
        String modeKey = shortlistModeKey(groupType);
        String valKey = shortlistValueKey(groupType);
        String mode = systemSettingRepository.findBySettingKey(modeKey)
                .map(SystemSetting::getSettingValue).orElse("RATIO");
        String val = systemSettingRepository.findBySettingKey(valKey)
                .map(SystemSetting::getSettingValue).orElse("0.55");
        double v = Double.parseDouble(val);
        if ("COUNT".equalsIgnoreCase(mode)) {
            return (int) Math.min(v, totalCount);
        }
        return (int) Math.round(totalCount * v);
    }

    private int total(GroupType gt, List<ScoringSnapshot> all) {
        return (int) all.stream().filter(s -> s.getGroupType() == gt).count();
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
