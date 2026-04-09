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
    // ---- 来自 user_accounts（只读展示）----
    private Long userId;
    private String name;
    private String phone;
    /** 职称：初级 / 中级 / 副高 / 正高，前端单选渲染 */
    private String title;
    private String institutionName;

    // ---- 来自 reviewer_profiles（可编辑）----
    private String gender;
    private String position;
    private String department;
    private String idNumber;
    private String idNumberMasked;
    private String idCardFrontUrl;
    private String idCardBackUrl;
    private String bankName;
    private String bankCardNo;
    private String bankCardNoMasked;
    private String backgroundsJson;
    private String backgroundsOther;
    private String toolsJson;
    private String toolsOther;
    private String topicsJson;
    private String topicsOther;
    /** 品管相关经验，多选 JSON 数组 */
    private String experienceJson;
}
