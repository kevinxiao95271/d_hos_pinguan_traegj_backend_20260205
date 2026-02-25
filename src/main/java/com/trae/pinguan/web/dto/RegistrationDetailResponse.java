package com.trae.pinguan.web.dto;

import com.trae.pinguan.web.dto.ActivityInfoDetailResponse;
import com.trae.pinguan.domain.entity.MaterialFile;
import com.trae.pinguan.domain.entity.ProjectSummary;
import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.entity.RegistrationMember;
import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.Builder;

@Data
@Builder
@AllArgsConstructor
public class RegistrationDetailResponse {
    @Schema(description = "报名基本信息")
    private Registration registration;
    
    @Schema(description = "赛事ID")
    private Long competitionId;
    
    @Schema(description = "赛事名称")
    private String competitionName;
    
    @Schema(description = "机构详细信息")
    private InstitutionInfo institution;
    
    @Schema(description = "成员列表")
    private List<RegistrationMember> members;
    
    @Schema(description = "活动说明详情")
    private ActivityInfoDetailResponse activityInfo;
    
    @Schema(description = "项目摘要")
    private ProjectSummary projectSummary;
    
    @Schema(description = "材料列表")
    private List<MaterialFile> materials;
}
