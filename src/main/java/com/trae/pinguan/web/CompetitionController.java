package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.Competition;
import com.trae.pinguan.service.CompetitionMaintenanceService;
import com.trae.pinguan.service.CompetitionService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.CompetitionCreateRequest;
import com.trae.pinguan.web.dto.CompetitionMergeRequest;
import com.trae.pinguan.web.dto.CompetitionMergeResponse;
import com.trae.pinguan.web.dto.CompetitionStageUpdateRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/competitions")
@RequiredArgsConstructor
@Tag(name = "赛事")
@SecurityRequirement(name = "BearerAuth")
public class CompetitionController {
    private final CompetitionService competitionService;
    private final CompetitionMaintenanceService competitionMaintenanceService;

    @GetMapping
    @Operation(summary = "赛事列表")
    public ApiResponse<List<Competition>> list() {
        return ApiResponse.ok(competitionService.listAll());
    }
    
    @GetMapping("/latest")
    @Operation(summary = "获取最新赛事", description = "返回ID最大的赛事，用作默认选中")
    public ApiResponse<Competition> latest() {
        return competitionService.getLatest()
                .map(ApiResponse::ok)
                .orElse(ApiResponse.fail("暂无赛事"));
    }

    @PostMapping
    @Operation(summary = "新增赛事")
    public ApiResponse<Competition> create(@Valid @RequestBody CompetitionCreateRequest request) {
        return ApiResponse.ok(competitionService.create(request));
    }

    @GetMapping("/{id}")
    @Operation(summary = "赛事详情")
    public ApiResponse<Competition> detail(@PathVariable Long id) {
        return ApiResponse.ok(competitionService.get(id));
    }

    @PutMapping("/{id}/stage")
    @Operation(summary = "更新赛事阶段")
    public ApiResponse<Competition> updateStage(@PathVariable Long id,
                                                @Valid @RequestBody CompetitionStageUpdateRequest request) {
        return ApiResponse.ok(competitionService.updateStage(id, request.getStage()));
    }

    @PostMapping("/merge")
    @Operation(summary = "合并赛事")
    public ApiResponse<CompetitionMergeResponse> merge(@Valid @RequestBody CompetitionMergeRequest request) {
        return ApiResponse.ok(competitionMaintenanceService.mergeCompetitions(request));
    }
}
