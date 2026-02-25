package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
@Schema(description = "创建报名请求")
public class RegistrationCreateRequest {
    @NotNull(message = "赛事ID不能为空")
    @Schema(description = "赛事ID", example = "1", required = true)
    private Long competitionId;
    
    @Schema(description = "机构ID（可选，不传则自动使用当前用户的所属机构）", example = "123")
    private Long institutionId;
    
    @Schema(description = "申请人ID（自动从token获取，前端不需要传）", hidden = true)
    private Long applicantId;
    
    @NotBlank(message = "项目名称不能为空")
    @Size(max = 100, message = "项目名称不能超过100个字符")
    @Schema(description = "项目名称", example = "品管圈改善案例", required = true)
    private String projectName;
    
    @NotNull(message = "组别不能为空")
    @Schema(description = "组别", example = "GENERAL", required = true)
    private GroupType groupType;
}
