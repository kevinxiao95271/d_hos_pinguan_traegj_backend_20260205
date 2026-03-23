package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@Schema(description = "入围统计结果（含本次计算配置摘要）")
public class ShortlistResult {

    // ── 基本信息 ────────────────────────────────────────────────
    @Schema(description = "本次查询的阶段：BOOK=书审，INTERVIEW=面谈")
    private String stage;

    @Schema(description = "最近一次快照计算时间")
    private LocalDateTime snapshotAt;

    @Schema(description = "总项目数")
    private int totalCount;

    @Schema(description = "总入围数（含人工干预）")
    private int shortlistCount;

    @Schema(description = "入围比例（shortlistCount / totalCount）")
    private double shortlistRatio;

    // ── 书审阶段：入围范围模式 ───────────────────────────────────
    @Schema(description = "书审入围范围模式：PER_GROUP=各组独立；UNIFIED=合并统一。面谈阶段为 null")
    private String scope;

    @Schema(description = "UNIFIED 模式下的计算方式：COUNT=取前N名，RATIO=按比例。非 UNIFIED 时为 null")
    private String unifiedMode;

    @Schema(description = "UNIFIED 模式下的配置值：COUNT 时为整数，RATIO 时为小数。非 UNIFIED 时为 null")
    private Double unifiedValue;

    @Schema(description = "UNIFIED 模式下实际计算出的入围线名次（纯规则，不含人工干预）")
    private Integer unifiedCutoff;

    // ── 各组别配置摘要 ────────────────────────────────────────
    @Schema(description = "各组别配置摘要，PER_GROUP 模式下包含每组的 mode/value/cutoff/total/withinLineCount")
    private List<Map<String, Object>> groupConfigs;

    // ── 明细列表 ──────────────────────────────────────────────
    @Schema(description = "入围明细列表")
    private List<ShortlistItem> items;
}
