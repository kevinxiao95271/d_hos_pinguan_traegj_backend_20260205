package com.trae.pinguan.web.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class ActivityInfoDetailResponse {
    private String theme;
    private String keywords;
    private String subjectTypeCode;
    private String subjectTypeOther;
    private String subjectTypeLabel;
    private String methodCode;
    private String methodOther;
    private String experienceImproveCode;
    private String experienceImproveOther;
    private String qualityTopicCode;
    private String qualityTopicOther;
    private Integer avgWorkYears;
    private Integer avgAge;
    private Boolean crossDepartment;
    private Boolean relatedToDigitalAi;
    private String methodLabel;
}
