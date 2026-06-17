package com.trae.pinguan.web.dto;

import java.util.List;
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
    private String reviewerGroupCode;
    private String interviewGroupCode;
    private String expertBackground;
    /** 已分配的决赛专场代码列表（需传 competitionId 才会填充，否则为空列表） */
    private List<String> finalSessionCodes;
}
