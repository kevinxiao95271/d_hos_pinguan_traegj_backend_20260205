package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ReviewStage;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ReviewResultItem {
    @Schema(example = "BOOK")
    private ReviewStage stage;
    @Schema(example = "2")
    private Integer taskCount;
    @Schema(example = "1")
    private Integer scoredCount;
    @Schema(example = "85.5")
    private Double avgTotal;
}
