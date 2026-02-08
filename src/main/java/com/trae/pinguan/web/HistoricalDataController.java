package com.trae.pinguan.web;

import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.service.HistoricalDataService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.HistoricalDataQueryRequest;
import com.trae.pinguan.web.dto.HistoricalDataResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;

/**
 * 历史数据控制器
 * 仅限组委会管理员和系统运维查看
 */
@RestController
@RequestMapping("/api/historical-data")
@RequiredArgsConstructor
@Tag(name = "历史数据", description = "历史数据查询接口（仅限COMMITTEE_ADMIN和OPS）")
@SecurityRequirement(name = "Bearer Authentication")
public class HistoricalDataController {
    
    private final HistoricalDataService historicalDataService;
    private final HttpServletRequest httpRequest;
    
    @GetMapping
    @Operation(summary = "查询历史数据", description = "支持多条件筛选和分页，仅限组委会管理员和系统运维")
    public ApiResponse<Page<HistoricalDataResponse>> queryHistoricalData(
            @Parameter(description = "地区关键词") @RequestParam(required = false) String region,
            @Parameter(description = "组别") @RequestParam(required = false) String competitionGroup,
            @Parameter(description = "品管工具/圈名") @RequestParam(required = false) String circleName,
            @Parameter(description = "入围状态") @RequestParam(required = false) String dataStatus,
            @Parameter(description = "医院名称") @RequestParam(required = false) String institutionName,
            @Parameter(description = "项目名称") @RequestParam(required = false) String projectName,
            @Parameter(description = "年份") @RequestParam(required = false) String year,
            @Parameter(description = "页码（从0开始）") @RequestParam(defaultValue = "0") Integer page,
            @Parameter(description = "每页大小") @RequestParam(defaultValue = "20") Integer size,
            @Parameter(description = "排序字段") @RequestParam(defaultValue = "id") String sortBy,
            @Parameter(description = "排序方向") @RequestParam(defaultValue = "DESC") String sortDirection
    ) {
        // 权限检查：仅限 COMMITTEE_ADMIN 和 OPS
        String role = getCurrentUserRole();
        if (!RoleType.COMMITTEE_ADMIN.name().equals(role) && !RoleType.OPS.name().equals(role)) {
            return ApiResponse.fail("无权访问历史数据，仅限组委会管理员和系统运维");
        }
        
        // 构建查询请求
        HistoricalDataQueryRequest request = new HistoricalDataQueryRequest();
        request.setRegion(region);
        request.setCompetitionGroup(competitionGroup);
        request.setCircleName(circleName);
        request.setDataStatus(dataStatus);
        request.setInstitutionName(institutionName);
        request.setProjectName(projectName);
        request.setYear(year);
        request.setPage(page);
        request.setSize(size);
        request.setSortBy(sortBy);
        request.setSortDirection(sortDirection);
        
        // 执行查询
        Page<HistoricalDataResponse> result = historicalDataService.queryHistoricalData(request);
        
        return ApiResponse.ok(result);
    }
    
    /**
     * 获取当前用户角色
     */
    private String getCurrentUserRole() {
        Object role = httpRequest.getAttribute("role");
        if (role == null) {
            throw new RuntimeException("未找到用户角色信息");
        }
        return role.toString();
    }
}
