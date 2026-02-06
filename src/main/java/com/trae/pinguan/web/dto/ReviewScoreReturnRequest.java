package com.trae.pinguan.web.dto;

import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class ReviewScoreReturnRequest {
    @NotNull
    private Long reviewTaskId;
}
