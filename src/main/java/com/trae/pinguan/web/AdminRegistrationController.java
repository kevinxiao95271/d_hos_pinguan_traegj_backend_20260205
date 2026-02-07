package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.service.RegistrationService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.AutoGroupRequest;
import com.trae.pinguan.web.dto.BatchClassificationRequest;
import com.trae.pinguan.web.dto.GroupedRegistrationResponse;
import com.trae.pinguan.web.dto.RegistrationFilterItem;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
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
    @Operation(summary = "后台报名筛选（支持按code或label筛选、分页）",
               description = "获取报名筛选列表，支持多维度筛选和分页：\n" +
                             "【筛选维度】\n" +
                             "1) 按竞赛组别筛选\n" +
                             "2) 按分组代码筛选\n" +
                             "3) 按项目名称筛选（模糊）\n" +
                             "4) 按机构名称筛选（模糊）\n" +
                             "5) 按品管工具筛选（支持code或label）\n" +
                             "6) 按课题类型筛选（支持code或label）\n\n" +
                             "【分页参数】\n" +
                             "- page: 页码（从1开始），不传则返回全部数据\n" +
                             "- size: 每页数量，默认20\n\n" +
                             "【返回格式】\n" +
                             "- 不分页: 返回数组 []\n" +
                             "- 分页: 返回对象 {content: [], pageNo: 1, pageSize: 20, totalCount: 100, ...}")
    public ApiResponse<?> filter(@RequestParam Long competitionId,
                                 @RequestParam(required = false) com.trae.pinguan.domain.enums.GroupType groupType,
                                 @RequestParam(required = false) String groupCode,
                                 @RequestParam(required = false) String projectName,
                                 @RequestParam(required = false) String institutionName,
                                 @RequestParam(required = false) String methodCode,
                                 @RequestParam(required = false) String methodLabel,
                                 @RequestParam(required = false) String subjectTypeCode,
                                 @RequestParam(required = false) String subjectTypeLabel,
                                 @RequestParam(required = false) Integer page,
                                 @RequestParam(required = false) Integer size) {
        return ApiResponse.ok(registrationService.filterRegistrations(
                competitionId,
                groupType,
                groupCode,
                projectName,
                institutionName,
                methodCode,
                methodLabel,
                subjectTypeCode,
                subjectTypeLabel,
                page,
                size
        ));
    }

    @GetMapping("/interview-groups")
    @Operation(summary = "后台面谈分组")
    public ApiResponse<List<GroupedRegistrationResponse>> interviewGroups(@RequestParam Long competitionId) {
        return ApiResponse.ok(registrationService.groupByGroupCode(competitionId));
    }

    @GetMapping("/final-groups")
    @Operation(summary = "后台决赛分组")
    public ApiResponse<List<GroupedRegistrationResponse>> finalGroups(@RequestParam Long competitionId) {
        return ApiResponse.ok(registrationService.groupByGroupCode(competitionId));
    }
}
