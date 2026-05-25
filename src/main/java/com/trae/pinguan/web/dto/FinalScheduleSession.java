package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "场次详情（含项目列表）")
public class FinalScheduleSession {

    @Schema(description = "日期，如 6.3 / 6.4 / 6.5")
    private String sessionDate;

    @Schema(description = "场次代码，如 综合组-问题解决型专场1")
    private String sessionCode;

    @Schema(description = "项目总数")
    private int totalCount;

    @Schema(description = "QCC 项目数")
    private int qccCount;

    @Schema(description = "QFD 项目数")
    private int qfdCount;

    @Schema(description = "非QCC 项目数")
    private int nonQccCount;

    @Schema(description = "项目列表（按上台顺序）")
    private List<FinalProjectItem> projects;
}
