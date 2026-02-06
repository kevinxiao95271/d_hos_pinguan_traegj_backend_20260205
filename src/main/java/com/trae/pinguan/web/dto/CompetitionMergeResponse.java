package com.trae.pinguan.web.dto;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class CompetitionMergeResponse {
    private Long targetCompetitionId;
    private List<Long> keptCompetitionIds;
    private List<Long> removedCompetitionIds;
    private Integer movedRegistrations;
}
