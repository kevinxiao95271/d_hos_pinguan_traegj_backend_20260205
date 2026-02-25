package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
@Schema(description = "更新报名请求")
public class RegistrationUpdateRequest {
    @Size(max = 100, message = "项目名称不能超过100个字符")
    @Schema(description = "项目名称", example = "品管圈改善案例")
    private String projectName;
    
    @Schema(description = "组别", example = "GENERAL")
    private GroupType groupType;
    
    @Schema(description = "机构ID（一般不建议修改，仅特殊情况使用）", example = "123")
    private Long institutionId;
}
