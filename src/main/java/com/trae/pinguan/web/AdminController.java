package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.SystemSetting;
import com.trae.pinguan.service.CompetitionMaintenanceService;
import com.trae.pinguan.service.DataSourceSwitchService;
import com.trae.pinguan.service.StatsService;
import com.trae.pinguan.service.SystemSettingService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.CompetitionMergeRequest;
import com.trae.pinguan.web.dto.CompetitionMergeResponse;
import com.trae.pinguan.web.dto.DataSourceSwitchRequest;
import com.trae.pinguan.web.dto.StatsSummaryResponse;
import com.trae.pinguan.web.dto.SystemSettingRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
@Tag(name = "后台管理")
@SecurityRequirement(name = "BearerAuth")
public class AdminController {
    private final DataSourceSwitchService dataSourceSwitchService;
    private final SystemSettingService systemSettingService;
    private final StatsService statsService;
    private final CompetitionMaintenanceService competitionMaintenanceService;

    @GetMapping("/datasource")
    @Operation(summary = "获取当前数据源")
    public ApiResponse<String> current() {
        return ApiResponse.ok(dataSourceSwitchService.current());
    }

    @PostMapping("/datasource/switch")
    @Operation(summary = "切换数据源")
    public ApiResponse<String> switchDataSource(@Valid @RequestBody DataSourceSwitchRequest request) {
        return ApiResponse.ok(dataSourceSwitchService.switchTo(request.getTarget()));
    }

    @PostMapping("/settings")
    @Operation(summary = "新增或更新系统设置")
    public ApiResponse<SystemSetting> upsertSetting(@Valid @RequestBody SystemSettingRequest request) {
        return ApiResponse.ok(systemSettingService.upsert(request));
    }

    @GetMapping("/settings")
    @Operation(summary = "获取系统设置")
    public ApiResponse<SystemSetting> getSetting(@RequestParam String key) {
        return ApiResponse.ok(systemSettingService.get(key));
    }

    @GetMapping("/stats/summary")
    @Operation(summary = "统计汇总")
    public ApiResponse<StatsSummaryResponse> summary(@RequestParam(required = false) Long competitionId) {
        if (competitionId != null) {
            return ApiResponse.ok(statsService.summaryForCompetition(competitionId));
        }
        return ApiResponse.ok(statsService.summaryForLatestCompetition());
    }

    @PostMapping("/competitions/merge")
    @Operation(summary = "合并赛事")
    public ApiResponse<CompetitionMergeResponse> mergeCompetitions(@Valid @RequestBody CompetitionMergeRequest request) {
        return ApiResponse.ok(competitionMaintenanceService.mergeCompetitions(request));
    }
    
    @PostMapping("/current-competition")
    @Operation(summary = "设置当前活跃赛事（全局）")
    public ApiResponse<String> setCurrentCompetition(@RequestParam Long competitionId) {
        systemSettingService.setCurrentCompetitionId(competitionId);
        return ApiResponse.ok("已设置当前赛事ID: " + competitionId);
    }
    
    @GetMapping("/current-competition")
    @Operation(summary = "获取当前活跃赛事ID（全局）")
    public ApiResponse<Long> getCurrentCompetition() {
        Long competitionId = systemSettingService.getCurrentCompetitionId();
        if (competitionId == null) {
            return ApiResponse.fail("未设置当前赛事");
        }
        return ApiResponse.ok(competitionId);
    }
}
