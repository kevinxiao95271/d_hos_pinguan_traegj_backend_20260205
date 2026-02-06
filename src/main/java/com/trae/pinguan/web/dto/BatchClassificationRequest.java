package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotEmpty;
import lombok.Data;

@Data
public class BatchClassificationRequest {
    @NotEmpty
    @Schema(example = "[1,2,3]")
    private List<Long> registrationIds;
    @NotBlank
    @Schema(example = "G1")
    private String groupCode;
}
