package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.RegistrationStatus;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MyRegistrationItem {
    private Long id;
    private Long competitionId;
    private Long institutionId;
    private String institutionName;
    private String institutionLevel;
    private Long applicantId;
    private String projectName;
    private GroupType groupType;
    private String groupCode;
    private RegistrationStatus status;
    private LocalDateTime submittedAt;
    private LocalDateTime createdAt;
}
