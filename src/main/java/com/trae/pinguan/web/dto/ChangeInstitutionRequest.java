package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
@Schema(description = "评委修改所属机构请求")
public class ChangeInstitutionRequest {

    @NotNull(message = "新机构ID不能为空")
    @Schema(description = "新所属机构ID")
    private Long newInstitutionId;

    @Size(max = 500, message = "原因长度不能超过500字")
    @Schema(description = "变更原因（选填）")
    private String reason;
}
