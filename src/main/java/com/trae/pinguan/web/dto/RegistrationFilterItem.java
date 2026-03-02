package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class RegistrationFilterItem {
    private Long id;
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
    
    private List<MaterialFileSimple> materials = new ArrayList<>();
    
    public RegistrationFilterItem(Long registrationId, String projectName, String institutionName,
                                  String institutionLevel, GroupType groupType, String groupCode,
                                  LocalDateTime submittedAt, String subjectTypeCode, String methodCode,
                                  String subjectTypeLabel, String methodLabel, String applicantName) {
        this.id = registrationId;
        this.registrationId = registrationId;
        this.projectName = projectName;
        this.institutionName = institutionName;
        this.institutionLevel = institutionLevel;
        this.groupType = groupType;
        this.groupCode = groupCode;
        this.submittedAt = submittedAt;
        this.subjectTypeCode = subjectTypeCode;
        this.methodCode = methodCode;
        this.subjectTypeLabel = subjectTypeLabel;
        this.methodLabel = methodLabel;
        this.applicantName = applicantName;
        this.materials = new ArrayList<>();
    }
    
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class MaterialFileSimple {
        private Long id;
        private String type;
        private String fileName;
        private String downloadUrl;
        private LocalDateTime uploadedAt;
    }
}
