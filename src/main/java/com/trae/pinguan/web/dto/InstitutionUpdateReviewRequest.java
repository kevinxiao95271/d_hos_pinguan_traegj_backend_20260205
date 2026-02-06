package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ApprovalStatus;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class InstitutionUpdateReviewRequest {
    @NotNull
    private Long requestId;
    @NotNull
    private ApprovalStatus status;
}
