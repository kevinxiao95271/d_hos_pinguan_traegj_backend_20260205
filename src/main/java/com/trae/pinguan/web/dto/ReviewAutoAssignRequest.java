package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ReviewStage;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class ReviewAutoAssignRequest {
    @NotNull
    @Schema(example = "21")
    private Long competitionId;
    @NotNull
    @Schema(example = "BOOK")
    private ReviewStage stage;
    @Schema(example = "2")
    private Integer reviewersPerRegistration;
}
