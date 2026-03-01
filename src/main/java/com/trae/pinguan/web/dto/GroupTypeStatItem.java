package com.trae.pinguan.web.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class GroupTypeStatItem {
    private String groupTypeName;
    private Integer institutionCount;
    private Integer projectCount;
    private Double projectPercentage;
    private Double avgProjectsPerInstitution;
}
