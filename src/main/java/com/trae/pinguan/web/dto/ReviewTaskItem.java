package com.trae.pinguan.web.dto;

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
    private ReviewStage stage;
    private ReviewStatus status;
    private LocalDateTime createdAt;
}
