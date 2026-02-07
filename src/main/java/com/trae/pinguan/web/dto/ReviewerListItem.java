package com.trae.pinguan.web.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ReviewerListItem {
    private Long id;
    private String phone;
    private String name;
    private String title;
    private Long institutionId;
    private String institutionName;
    private String institutionLevel;
    private String reviewerGroupCode;
    private String interviewGroupCode;
    private String expertBackground;
}
