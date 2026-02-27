package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class GroupedRegistrationItem {
    @Schema(example = "101", description = "报名ID（与registrationId相同）")
    private Long id;
    @Schema(example = "101", description = "报名ID")
    private Long registrationId;
    @Schema(example = "项目A")
    private String projectName;
    @Schema(example = "某医院")
    private String institutionName;
    @Schema(example = "三级甲等")
    private String institutionLevel;
    @Schema(example = "BASIC")
    private GroupType groupType;
    @Schema(example = "M1")
    private String groupCode;
    @Schema(example = "2026-02-26T10:30:00", description = "报名提交时间")
    private LocalDateTime submittedAt;
    
    public GroupedRegistrationItem(Long registrationId, String projectName, String institutionName, 
                                   String institutionLevel, GroupType groupType, String groupCode, 
                                   LocalDateTime submittedAt) {
        this.id = registrationId;
        this.registrationId = registrationId;
        this.projectName = projectName;
        this.institutionName = institutionName;
        this.institutionLevel = institutionLevel;
        this.groupType = groupType;
        this.groupCode = groupCode;
        this.submittedAt = submittedAt;
    }
}
