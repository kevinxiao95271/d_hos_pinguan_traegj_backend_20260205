package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "现场竞赛专场信息")
public class FinalSessionItem {

    @Schema(description = "日期，如 6.3 / 6.4 / 6.5")
    private String sessionDate;

    @Schema(description = "专场代码，如 综合组-问题解决型专场1")
    private String sessionCode;

    @Schema(description = "该专场项目总数")
    private int totalCount;

    @Schema(description = "QCC 项目数")
    private int qccCount;

    @Schema(description = "QFD 项目数")
    private int qfdCount;

    @Schema(description = "非QCC 项目数")
    private int nonQccCount;
}
