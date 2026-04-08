package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
@Schema(description = "面谈评分提交请求")
public class InterviewScoreRequest {

    @NotNull
    @Schema(description = "评审任务ID")
    private Long reviewTaskId;

    @NotNull
    @Schema(description = "选题（迫切性、实用性、可行性），满分10")
    private Double topic;

    @NotNull
    @Schema(description = "改善过程的确实性（书面资料一致性、原始数据、成员了解、工具运用），满分40")
    private Double process;

    @NotNull
    @Schema(description = "整体运作（团队运作、参与积极性、创新性、培训成长、改善经历），满分20")
    private Double operation;

    @NotNull
    @Schema(description = "改善成果（成效确实性、标准化落实、对医院/患者贡献），满分30")
    private Double result;

    @Size(max = 1000, message = "亮点不能超过1000字")
    @Schema(description = "亮点（选填，最多1000字）")
    private String highlight;

    @Size(max = 1000, message = "建议不能超过1000字")
    @Schema(description = "建议（选填，最多1000字）")
    private String weakness;
}
