package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "现场竞赛专场内项目信息")
public class FinalProjectItem {

    @Schema(description = "报名 ID")
    private Long registrationId;

    @Schema(description = "专场内上台顺序")
    private Integer sessionOrder;

    @Schema(description = "项目名称")
    private String projectName;

    @Schema(description = "机构名称")
    private String institutionName;

    @Schema(description = "组别代码，如 B1")
    private String groupCode;

    @Schema(description = "评分表类型：QCC / NON_QCC / QFD")
    private String scoreForm;
}
