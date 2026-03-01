package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.service.RegistrationService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.AutoGroupRequest;
import com.trae.pinguan.web.dto.BatchClassificationRequest;
import com.trae.pinguan.web.dto.GroupedRegistrationResponse;
import com.trae.pinguan.web.dto.RegistrationFilterItem;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import com.trae.pinguan.web.dto.PageResult;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin/registrations")
@RequiredArgsConstructor
@Tag(name = "后台报名")
@SecurityRequirement(name = "BearerAuth")
public class AdminRegistrationController {
    private final RegistrationService registrationService;

    @PostMapping("/batch-classify")
    @Operation(summary = "后台批量分类")
    public ApiResponse<List<Registration>> batchClassify(@Valid @RequestBody BatchClassificationRequest request) {
        return ApiResponse.ok(registrationService.batchClassify(request));
    }

    @PostMapping("/auto-group")
    @Operation(summary = "后台自动分组")
    public ApiResponse<List<Registration>> autoGroup(@Valid @RequestBody AutoGroupRequest request) {
        return ApiResponse.ok(registrationService.autoGroup(request));
    }

    @GetMapping("/filter")
    @Operation(summary = "后台报名筛选（分页，page从1开始）")
    public ApiResponse<PageResult<RegistrationFilterItem>> filter(@RequestParam Long competitionId,
                                                                  @RequestParam(required = false) com.trae.pinguan.domain.enums.GroupType groupType,
                                                                  @RequestParam(required = false) String groupCode,
                                                                  @RequestParam(required = false) String projectName,
                                                                  @RequestParam(required = false) String institutionName,
                                                                  @RequestParam(required = false) String methodCode,
                                                                  @RequestParam(required = false) String subjectTypeCode,
                                                                  @RequestParam(defaultValue = "1") int page,
                                                                  @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.ok(PageResult.of(registrationService.filterRegistrations(
                competitionId,
                groupType,
                groupCode,
                projectName,
                institutionName,
                methodCode,
                subjectTypeCode,
                page,
                size
        )));
    }

    @GetMapping("/interview-groups")
    @Operation(summary = "后台面谈分组（仅进阶组）")
    public ApiResponse<List<GroupedRegistrationResponse>> interviewGroups(@RequestParam Long competitionId) {
        return ApiResponse.ok(registrationService.groupByGroupCode(competitionId, com.trae.pinguan.domain.enums.GroupType.ADVANCED));
    }

    @GetMapping("/final-groups")
    @Operation(summary = "后台决赛分组")
    public ApiResponse<List<GroupedRegistrationResponse>> finalGroups(@RequestParam Long competitionId) {
        return ApiResponse.ok(registrationService.groupByGroupCode(competitionId));
    }
    
    @PostMapping("/fix-invalid-codes")
    @Operation(summary = "修复无效的字典code（临时维护接口）")
    public ApiResponse<String> fixInvalidCodes() {
        String result = registrationService.fixInvalidDictionaryCodes();
        return ApiResponse.ok(result);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除报名（仅OPS）", description = "级联删除报名及所有关联数据，仅供测试数据清理")
    public ApiResponse<String> deleteRegistration(
            @Parameter(description = "报名ID", required = true) @PathVariable Long id,
            HttpServletRequest request) {
        String role = (String) request.getAttribute("role");
        if (!RoleType.OPS.name().equals(role)) {
            return ApiResponse.fail("仅系统运维可操作");
        }
        try {
            registrationService.deleteRegistration(id);
            return ApiResponse.ok("报名已删除");
        } catch (IllegalArgumentException e) {
            return ApiResponse.fail(e.getMessage());
        }
    }
}
