package com.trae.pinguan.web;

import com.trae.pinguan.service.MaterialService;
import com.trae.pinguan.web.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/materials")
@RequiredArgsConstructor
@Tag(name = "报名材料")
@SecurityRequirement(name = "BearerAuth")
public class MaterialController {
    private final MaterialService materialService;

    @DeleteMapping("/{id}")
    @Operation(summary = "删除材料")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        materialService.delete(id);
        return ApiResponse.ok(null);
    }
}
