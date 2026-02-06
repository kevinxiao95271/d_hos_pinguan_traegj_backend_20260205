package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.InstitutionUpdateRequest;
import com.trae.pinguan.service.InstitutionUpdateService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.InstitutionUpdateReviewRequest;
import com.trae.pinguan.web.dto.InstitutionUpdateSubmitRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/institution-updates")
@RequiredArgsConstructor
@Tag(name = "机构维护")
@SecurityRequirement(name = "BearerAuth")
public class InstitutionUpdateController {
    private final InstitutionUpdateService institutionUpdateService;

    @PostMapping
    @Operation(summary = "提交机构信息维护申请")
    public ApiResponse<InstitutionUpdateRequest> submit(@Valid @RequestBody InstitutionUpdateSubmitRequest request) {
        return ApiResponse.ok(institutionUpdateService.submit(request));
    }

    @PostMapping("/review")
    @Operation(summary = "审核机构信息维护申请")
    public ApiResponse<InstitutionUpdateRequest> review(@Valid @RequestBody InstitutionUpdateReviewRequest request) {
        return ApiResponse.ok(institutionUpdateService.review(request));
    }

    @GetMapping("/pending")
    @Operation(summary = "待审机构维护申请列表")
    public ApiResponse<List<InstitutionUpdateRequest>> listPending() {
        return ApiResponse.ok(institutionUpdateService.listPending());
    }
}
