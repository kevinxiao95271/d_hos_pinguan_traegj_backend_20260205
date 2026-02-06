package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.CompetitionStage;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class CompetitionStageUpdateRequest {
    @NotNull
    private CompetitionStage stage;
}
