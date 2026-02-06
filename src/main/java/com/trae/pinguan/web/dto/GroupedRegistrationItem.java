package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class GroupedRegistrationItem {
    @Schema(example = "101")
    private Long registrationId;
    @Schema(example = "项目A")
    private String projectName;
    @Schema(example = "某医院")
    private String institutionName;
    @Schema(example = "BASIC")
    private GroupType groupType;
    @Schema(example = "M1")
    private String groupCode;
}
