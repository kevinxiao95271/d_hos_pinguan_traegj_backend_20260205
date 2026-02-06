package com.trae.pinguan.web.dto;

import java.util.List;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class CompetitionMergeRequest {
    @NotNull
    private Long targetCompetitionId;
    @NotNull
    private List<Long> keepCompetitionIds;
    private Boolean moveAllRegistrationsToTarget;
}
