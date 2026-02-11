package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStatus;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BookScoreItem {
    // 任务信息
    private Long taskId;
    private ReviewStatus status;
    private LocalDateTime createdAt;
    
    // 报名项目信息
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private String institutionLevel;
    private GroupType groupType;
    private String groupCode;
    
    // 评委信息
    private Long reviewerId;
    private String reviewerName;
    private String reviewerTitle;
    private String reviewerInstitutionName;
    
    // 评分详情
    private Long scoreId;
    private Double plan;
    private Double problem;
    private Double action;
    private Double success;
    private Double review;
    private Double operation;
    private Double presentation;
    private Double total;
    private LocalDateTime submittedAt;
}
