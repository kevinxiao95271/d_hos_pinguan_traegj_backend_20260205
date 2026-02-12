package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GroupTypeStats {
    private GroupType groupType;
    private String groupTypeName;
    private Integer institutionCount;
    private Integer projectCount;
    private Double projectPercentage;
    private Double avgProjectsPerInstitution;
}
