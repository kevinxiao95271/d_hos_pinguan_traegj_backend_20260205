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
public class ReviewTaskItem {
    private Long id;
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private String institutionLevel;
    private GroupType groupType;
    private String groupCode;
    private ReviewStage stage;
    private ReviewStatus status;
    private LocalDateTime createdAt;
    
    // 评委信息
    private Long reviewerId;
    private String reviewerName;
    private String reviewerTitle;  // 评委职称
    private String reviewerInstitutionName;
    
    // 品管工具信息
    private String methodCode;
    private String methodLabel;
}
