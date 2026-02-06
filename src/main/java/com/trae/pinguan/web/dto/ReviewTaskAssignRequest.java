package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ReviewStage;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class ReviewTaskAssignRequest {
    @NotNull
    @Schema(example = "11")
    private Long registrationId;
    @NotNull
    @Schema(example = "14")
    private Long reviewerId;
    @NotNull
    @Schema(example = "BOOK")
    private ReviewStage stage;
}
