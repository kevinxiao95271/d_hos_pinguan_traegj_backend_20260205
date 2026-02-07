package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class RegistrationFilterItem {
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private String institutionLevel;
    private GroupType groupType;
    private String groupCode;
    private LocalDateTime submittedAt;
    private String subjectTypeCode;
    private String methodCode;
    private String subjectTypeLabel;
    private String methodLabel;
    private String applicantName;
}
