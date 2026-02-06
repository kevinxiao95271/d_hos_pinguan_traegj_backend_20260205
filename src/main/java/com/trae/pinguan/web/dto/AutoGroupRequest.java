package com.trae.pinguan.web.dto;

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
