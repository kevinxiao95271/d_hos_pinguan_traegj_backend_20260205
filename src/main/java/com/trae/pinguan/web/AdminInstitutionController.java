package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.service.InstitutionService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.InstitutionImportRequest;
import com.trae.pinguan.web.dto.InstitutionImportPrecheckResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/admin/institutions")
@RequiredArgsConstructor
@Tag(name = "后台机构")
@SecurityRequirement(name = "BearerAuth")
public class AdminInstitutionController {
    private final InstitutionService institutionService;
    private final HttpServletRequest request;

    private void requireOpsRole() {
        Object roleObj = request.getAttribute("role");
        String role = roleObj == null ? null : roleObj.toString();
        if (!"OPS".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "无权限");
        }
    }

    @GetMapping
    @Operation(summary = "机构列表查询（支持分页和筛选）",
               description = "获取机构列表，支持多维度筛选和分页：\n" +
                             "【筛选参数】\n" +
                             "- region: 地区筛选（精确匹配）\n" +
                             "- level: 等级筛选（精确匹配）\n" +
                             "- name: 名称搜索（模糊匹配）\n" +
                             "- unknownRegionOnly: 是否只显示未知地区\n\n" +
                             "【分页参数】\n" +
                             "- page: 页码（从1开始），不传则返回全部数据\n" +
                             "- size: 每页数量，默认20\n\n" +
                             "【返回格式】\n" +
                             "- 不分页: 返回数组 []\n" +
                             "- 分页: 返回对象 {content: [], pageNo: 1, pageSize: 20, totalCount: 100, ...}")
    public ApiResponse<?> list(@RequestParam(required = false) String region,
                               @RequestParam(required = false) String level,
                               @RequestParam(required = false) String name,
                               @RequestParam(required = false, defaultValue = "false") Boolean unknownRegionOnly,
                               @RequestParam(required = false) Integer page,
                               @RequestParam(required = false) Integer size) {
        requireOpsRole();
        return ApiResponse.ok(institutionService.listInstitutions(region, level, name, unknownRegionOnly, page, size));
    }
    
    @GetMapping("/export")
    @Operation(summary = "导出机构列表",
               deprecated = true,
               description = "⚠️ 已废弃：请使用 GET /api/admin/institutions 代替。新API支持更强大的筛选和分页功能。")
    @Deprecated
    public ApiResponse<List<Institution>> export(@RequestParam(required = false, defaultValue = "false") Boolean unknownRegionOnly) {
        requireOpsRole();
        List<Institution> all = institutionService.listAll();
        if (unknownRegionOnly != null && unknownRegionOnly) {
            List<Institution> filtered = new ArrayList<>();
            for (Institution inst : all) {
                if (inst.getRegion() == null || inst.getRegion().trim().isEmpty()) {
                    filtered.add(inst);
                }
            }
            return ApiResponse.ok(filtered);
        }
        return ApiResponse.ok(all);
    }

    @PostMapping("/import/precheck")
    @Operation(summary = "机构导入预检（不落库）")
    public ApiResponse<InstitutionImportPrecheckResponse> importPrecheck(@Valid @RequestBody InstitutionImportRequest requestBody) {
        requireOpsRole();
        List<Institution> existing = institutionService.listAll();
        Set<String> existingNames = new HashSet<>();
        Set<String> existingUscc = new HashSet<>();
        for (Institution inst : existing) {
            existingNames.add(inst.getName());
            existingUscc.add(inst.getUscc());
        }
        List<InstitutionImportPrecheckResponse.DuplicateItem> duplicates = new ArrayList<>();
        List<InstitutionImportRequest.InstitutionItem> candidates = requestBody.getItems();
        int willCreate = 0;
        for (InstitutionImportRequest.InstitutionItem item : candidates) {
            boolean nameDup = item.getName() != null && existingNames.contains(item.getName());
            boolean usccDup = item.getUscc() != null && existingUscc.contains(item.getUscc());
            if (nameDup || usccDup) {
                duplicates.add(new InstitutionImportPrecheckResponse.DuplicateItem(item.getName(), item.getUscc(), nameDup, usccDup));
            } else {
                willCreate += 1;
            }
        }
        InstitutionImportPrecheckResponse resp = new InstitutionImportPrecheckResponse(duplicates, willCreate, candidates.size());
        return ApiResponse.ok(resp);
    }

    @PostMapping("/import/confirm")
    @Operation(summary = "机构导入确认（落库，仅导入非重复项）")
    public ApiResponse<List<Institution>> importConfirm(@Valid @RequestBody InstitutionImportRequest requestBody) {
        requireOpsRole();
        List<Institution> existing = institutionService.listAll();
        Set<String> existingNames = new HashSet<>();
        Set<String> existingUscc = new HashSet<>();
        for (Institution inst : existing) {
            existingNames.add(inst.getName());
            existingUscc.add(inst.getUscc());
        }
        InstitutionImportRequest filtered = new InstitutionImportRequest();
        List<InstitutionImportRequest.InstitutionItem> items = new ArrayList<>();
        for (InstitutionImportRequest.InstitutionItem item : requestBody.getItems()) {
            boolean nameDup = item.getName() != null && existingNames.contains(item.getName());
            boolean usccDup = item.getUscc() != null && existingUscc.contains(item.getUscc());
            if (!nameDup && !usccDup) {
                items.add(item);
            }
        }
        filtered.setItems(items);
        return ApiResponse.ok(institutionService.importInstitutions(filtered));
    }

    @PutMapping("/{id}/region")
    @Operation(summary = "更新机构地区")
    public ApiResponse<Institution> updateRegion(@PathVariable Long id, @RequestParam String region) {
        requireOpsRole();
        com.trae.pinguan.web.dto.InstitutionUpdateRequest req = new com.trae.pinguan.web.dto.InstitutionUpdateRequest();
        req.setRegion(region);
        return ApiResponse.ok(institutionService.update(id, req));
    }
}
