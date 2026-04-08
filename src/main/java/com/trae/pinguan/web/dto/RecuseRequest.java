package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
@Schema(description = "评委申请规避评审任务")
public class RecuseRequest {

    @NotBlank(message = "规避原因code不能为空")
    @Schema(description = "规避原因字典code，来自 GET /api/dictionaries/recuse_reason", example = "GUIDED_PROJECT")
    private String reasonCode;

    @Size(max = 255, message = "规避原因说明不能超过255字")
    @Schema(description = "规避具体说明，reasonCode=OTHER 时必填")
    private String reasonOther;
}
