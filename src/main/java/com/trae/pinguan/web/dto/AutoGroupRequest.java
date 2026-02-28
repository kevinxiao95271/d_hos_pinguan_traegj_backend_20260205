package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.RegistrationStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class AutoGroupRequest {
    @NotNull
    @Schema(example = "21")
    private Long competitionId;
    
    @Schema(description = "组别类型（可选）：BASIC-基层组, COMPREHENSIVE-综合组, ADVANCED-进阶组。如果不指定，则对所有组别执行分组", example = "BASIC")
    private GroupType groupType;
    
    @NotBlank
    @Schema(example = "M")
    private String groupPrefix;
    @NotNull
    @Min(1)
    @Schema(example = "6")
    private Integer groupSize;
    @Schema(example = "APPROVED")
    private RegistrationStatus status;
}
