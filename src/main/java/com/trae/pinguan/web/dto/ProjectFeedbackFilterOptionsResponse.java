package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import java.util.List;
import java.util.Map;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProjectFeedbackFilterOptionsResponse {
    private List<GroupType> groupTypes;
    private Map<GroupType, List<String>> groupCodesByGroupType;
    private List<String> groupCodes;
}
