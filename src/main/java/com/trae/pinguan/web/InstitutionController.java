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
@SecurityRequirement(name = "BearerAuth")
public class InstitutionController {
    private final InstitutionService institutionService;

    @GetMapping
    @Operation(summary = "机构列表")
    public ApiResponse<List<Institution>> list() {
        return ApiResponse.ok(institutionService.listAll());
    }

    @GetMapping("/{id}")
    @Operation(summary = "机构详情")
    public ApiResponse<Institution> detail(@PathVariable Long id) {
        return ApiResponse.ok(institutionService.get(id));
    }

    @PostMapping
    @Operation(summary = "新增机构")
    public ApiResponse<Institution> create(@Valid @RequestBody InstitutionCreateRequest request) {
        return ApiResponse.ok(institutionService.create(request));
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新机构")
    public ApiResponse<Institution> update(@PathVariable Long id,
                                           @Valid @RequestBody InstitutionUpdateRequest request) {
        return ApiResponse.ok(institutionService.update(id, request));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除机构")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        institutionService.delete(id);
        return ApiResponse.ok(null);
    }

    @PostMapping("/import")
    @Operation(summary = "批量导入机构")
    public ApiResponse<List<Institution>> importInstitutions(@Valid @RequestBody InstitutionImportRequest request) {
        return ApiResponse.ok(institutionService.importInstitutions(request));
    }
}
