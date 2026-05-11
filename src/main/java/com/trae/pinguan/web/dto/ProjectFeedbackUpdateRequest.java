package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
public class ProjectFeedbackUpdateRequest {
    @Size(max = 5000, message = "亮点汇总不能超过5000字")
    @Schema(description = "组委会编辑后的亮点")
    private String highlight;

    @Size(max = 5000, message = "不足汇总不能超过5000字")
    @Schema(description = "组委会编辑后的不足")
    private String weakness;
}
