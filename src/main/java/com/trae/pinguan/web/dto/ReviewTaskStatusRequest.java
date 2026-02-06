package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ReviewStatus;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class ReviewTaskStatusRequest {
    @NotNull
    @Schema(example = "101")
    private Long reviewTaskId;
    @NotNull
    @Schema(example = "CONFIRMED")
    private ReviewStatus status;
}
