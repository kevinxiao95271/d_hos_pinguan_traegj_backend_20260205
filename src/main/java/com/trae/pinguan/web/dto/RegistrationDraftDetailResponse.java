package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.entity.RegistrationDraft;
import com.trae.pinguan.domain.entity.RegistrationDraftMember;
import com.trae.pinguan.domain.entity.RegistrationDraftMaterialFile;
import com.trae.pinguan.domain.entity.RegistrationDraftProjectSummary;
import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@AllArgsConstructor
public class RegistrationDraftDetailResponse {
    @Schema(description = "草稿基本信息")
    private RegistrationDraft draft;

    @Schema(description = "赛事ID")
    private Long competitionId;

    @Schema(description = "赛事名称")
    private String competitionName;

    @Schema(description = "机构详细信息")
    private InstitutionInfo institution;

    @Schema(description = "成员列表")
    private List<RegistrationDraftMember> members;

    @Schema(description = "活动说明详情")
    private ActivityInfoDetailResponse activityInfo;

    @Schema(description = "项目摘要")
    private RegistrationDraftProjectSummary projectSummary;

    @Schema(description = "材料列表（不含缴费回执）")
    private List<RegistrationDraftMaterialFile> materials;

    @Schema(description = "缴费回执列表")
    private List<RegistrationDraftMaterialFile> paymentProofs;
}
