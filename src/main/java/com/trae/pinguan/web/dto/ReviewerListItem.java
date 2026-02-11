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
    // 删除reviewerGroupCode和interviewGroupCode - 评审专家没有分组限制
    private String expertBackground;  // 专业背景（这才是分配的关键依据）
    private Integer currentLoad;  // 当前负荷（已分配任务数）
}
