package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.service.InstitutionService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.InstitutionCreateRequest;
import com.trae.pinguan.web.dto.InstitutionImportRequest;
import com.trae.pinguan.web.dto.InstitutionUpdateRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/institutions")
@RequiredArgsConstructor
@Tag(name = "机构")
public class InstitutionController {
    private final InstitutionService institutionService;
    private final com.trae.pinguan.service.ConstInitInstitutionService constInitInstitutionService;

    @GetMapping
    @SecurityRequirement(name = "BearerAuth")
    @Operation(
        summary = "机构列表（已禁用）", 
        description = "❌ 此接口已禁用！请使用 POST /api/institutions/search，支持分页和筛选。",
        deprecated = true
    )
    public ApiResponse<?> list() {
        return ApiResponse.fail("此接口已禁用，请使用 POST /api/institutions/search 进行查询。数据量过大(36K+)，必须使用分页。");
    }
    
    @PostMapping("/search")
    @Operation(
        summary = "🚀 注册搜索（推荐用于注册）", 
        description = "✅ 公开接口，注册时使用。从36K+机构库中搜索，支持关键词、地区、等级筛选和分页。性能优化，无卡顿。"
    )
    public ApiResponse<org.springframework.data.domain.Page<com.trae.pinguan.web.dto.InstitutionSimpleDTO>> searchV2(
            @RequestBody com.trae.pinguan.web.dto.InstitutionSearchRequest request
    ) {
        // 使用 const_init_institutions 表（36K+，轻量级查询）
        org.springframework.data.domain.Page<com.trae.pinguan.domain.entity.ConstInitInstitution> page = 
            constInitInstitutionService.search(
                request.getKeyword(),
                request.getRegion(),
                request.getLevel(),
                request.getPage(),
                request.getSize(),
                request.getSortBy(),
                request.getSortDirection()
            );
        
        // 转换为DTO
        org.springframework.data.domain.Page<com.trae.pinguan.web.dto.InstitutionSimpleDTO> dtoPage = 
            page.map(inst -> {
                String uscc = inst.getUscc();
                String usccLast4 = uscc != null && uscc.length() >= 4 
                    ? uscc.substring(uscc.length() - 4) 
                    : "";
                
                String displayText = inst.getName();
                if (inst.getRegion() != null) {
                    displayText += " (" + inst.getRegion() + ")";
                }
                if (inst.getLevel() != null && !"未定等".equals(inst.getLevel())) {
                    displayText += " [" + inst.getLevel() + "]";
                }
                
                return com.trae.pinguan.web.dto.InstitutionSimpleDTO.builder()
                    .id(inst.getId())  // 注意：这是 const_init_institutions 的 ID
                    .name(inst.getName())
                    .region(inst.getRegion())
                    .level(inst.getLevel())
                    .usccLast4(usccLast4)
                    .displayText(displayText)
                    .build();
            });
        
        return ApiResponse.ok(dtoPage);
    }
    
    @GetMapping("/search")
    @Operation(summary = "搜索机构（兼容旧版）", description = "✅ 公开接口。按名称或地区搜索，支持模糊匹配")
    public ApiResponse<org.springframework.data.domain.Page<Institution>> search(
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        return ApiResponse.ok(institutionService.search(keyword, page, size));
    }
    
    @GetMapping("/autocomplete")
    @Operation(
        summary = "🔍 自动完成",
        description = "✅ 公开接口，注册时可用。根据名称前缀快速查找机构，用于输入建议。最多返回20条"
    )
    public ApiResponse<List<com.trae.pinguan.web.dto.InstitutionSimpleDTO>> autocomplete(
            @RequestParam String prefix
    ) {
        org.springframework.data.domain.Page<Institution> page = institutionService.autocomplete(prefix, 20);
        List<com.trae.pinguan.web.dto.InstitutionSimpleDTO> result = page.getContent()
            .stream()
            .map(com.trae.pinguan.web.dto.InstitutionSimpleDTO::from)
            .collect(java.util.stream.Collectors.toList());
        return ApiResponse.ok(result);
    }
    
    @GetMapping("/cities")
    @Operation(
        summary = "🏙️ 获取市级列表", 
        description = "✅ 公开接口，注册时可用。返回浙江省11个地级市，推荐用于地区筛选"
    )
    public ApiResponse<List<String>> getCities() {
        return ApiResponse.ok(com.trae.pinguan.util.RegionUtils.getAllCities());
    }
    
    @GetMapping("/regions")
    @Operation(summary = "获取所有地区列表（区县级）", description = "✅ 公开接口。返回96个区县名称")
    public ApiResponse<List<String>> getRegions() {
        return ApiResponse.ok(institutionService.getAllRegions());
    }
    
    @GetMapping("/districts")
    @Operation(
        summary = "获取指定市的区县列表",
        description = "✅ 公开接口。根据城市名称返回其下辖区县"
    )
    public ApiResponse<List<String>> getDistricts(@RequestParam String city) {
        return ApiResponse.ok(com.trae.pinguan.util.RegionUtils.getDistrictsByCity(city));
    }
    
    @GetMapping("/levels")
    @Operation(summary = "获取所有等级列表", description = "✅ 公开接口，注册时可用")
    public ApiResponse<List<String>> getLevels() {
        return ApiResponse.ok(institutionService.getAllLevels());
    }
    
    @GetMapping("/hot-regions")
    @Operation(
        summary = "🔥 热门地区",
        description = "✅ 公开接口，注册时可用。返回机构数量最多的前N个地区，用于首页推荐"
    )
    public ApiResponse<List<java.util.Map<String, Object>>> getHotRegions(
            @RequestParam(defaultValue = "10") int limit
    ) {
        List<Object[]> results = institutionService.getHotRegions(limit);
        List<java.util.Map<String, Object>> hotRegions = results.stream()
            .map(row -> {
                java.util.Map<String, Object> map = new java.util.HashMap<>();
                map.put("region", row[0]);
                map.put("count", row[1]);
                return map;
            })
            .collect(java.util.stream.Collectors.toList());
        return ApiResponse.ok(hotRegions);
    }
    
    @GetMapping("/region-stats")
    @Operation(summary = "📊 地区统计", description = "✅ 公开接口。各地区机构数量统计")
    public ApiResponse<List<java.util.Map<String, Object>>> getRegionStats() {
        List<Object[]> results = institutionService.getRegionStats();
        List<java.util.Map<String, Object>> stats = results.stream()
            .map(row -> {
                java.util.Map<String, Object> map = new java.util.HashMap<>();
                map.put("region", row[0]);
                map.put("count", row[1]);
                return map;
            })
            .collect(java.util.stream.Collectors.toList());
        return ApiResponse.ok(stats);
    }
    
    @GetMapping("/by-uscc/{uscc}")
    @Operation(summary = "根据USCC查询机构", description = "✅ 公开接口")
    public ApiResponse<Institution> getByUscc(@PathVariable String uscc) {
        Institution inst = institutionService.findByUscc(uscc);
        if (inst == null) {
            return ApiResponse.fail("机构不存在");
        }
        return ApiResponse.ok(inst);
    }
    
    @GetMapping("/by-region/{region}")
    @SecurityRequirement(name = "BearerAuth")
    @Operation(summary = "按地区查询机构列表", description = "⚠️ 单个地区可能有上千条数据，建议使用search接口，需要认证")
    public ApiResponse<List<Institution>> getByRegion(@PathVariable String region) {
        return ApiResponse.ok(institutionService.findByRegion(region));
    }

    @GetMapping("/{id}")
    @Operation(summary = "机构详情", description = "✅ 公开接口")
    public ApiResponse<Institution> detail(@PathVariable Long id) {
        return ApiResponse.ok(institutionService.get(id));
    }

    @PostMapping
    @SecurityRequirement(name = "BearerAuth")
    @Operation(summary = "新增机构", description = "🔒 需要管理员权限")
    public ApiResponse<Institution> create(@Valid @RequestBody InstitutionCreateRequest request) {
        return ApiResponse.ok(institutionService.create(request));
    }

    @PutMapping("/{id}")
    @SecurityRequirement(name = "BearerAuth")
    @Operation(summary = "更新机构", description = "🔒 需要管理员权限")
    public ApiResponse<Institution> update(@PathVariable Long id,
                                           @Valid @RequestBody InstitutionUpdateRequest request) {
        return ApiResponse.ok(institutionService.update(id, request));
    }

    @DeleteMapping("/{id}")
    @SecurityRequirement(name = "BearerAuth")
    @Operation(summary = "删除机构", description = "🔒 需要管理员权限")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        institutionService.delete(id);
        return ApiResponse.ok(null);
    }

    @PostMapping("/import")
    @SecurityRequirement(name = "BearerAuth")
    @Operation(summary = "批量导入机构", description = "🔒 需要管理员权限")
    public ApiResponse<List<Institution>> importInstitutions(@Valid @RequestBody InstitutionImportRequest request) {
        return ApiResponse.ok(institutionService.importInstitutions(request));
    }
}
