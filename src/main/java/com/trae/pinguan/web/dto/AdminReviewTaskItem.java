package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
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
public class AdminReviewTaskItem {
    // 任务信息
    private Long id;
    private ReviewStage stage;
    private ReviewStatus status;
    private LocalDateTime createdAt;
    
    // 报名信息
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private GroupType groupType;
    private String groupCode;
    
    // 评委信息
    private Long reviewerId;
    private String reviewerName;
    private String reviewerTitle;
    private String reviewerInstitutionName;
    private String reviewerGroupCode;
    private String interviewGroupCode;
    private String expertBackground;
}
