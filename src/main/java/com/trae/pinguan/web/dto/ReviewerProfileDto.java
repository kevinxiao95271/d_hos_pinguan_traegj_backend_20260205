package com.trae.pinguan.web.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewerProfileDto {
    private Long userId;
    private String gender;
    private String position;
    private String idNumber;
    private String idNumberMasked;
    private String idCardFrontUrl;
    private String idCardBackUrl;
    private String bankName;
    private String bankCardNo;
    private String bankCardNoMasked;
    private String backgroundsJson;
    private String toolsJson;
    private String topicsJson;
}
