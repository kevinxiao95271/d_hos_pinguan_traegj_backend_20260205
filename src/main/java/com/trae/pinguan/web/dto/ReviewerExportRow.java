package com.trae.pinguan.web.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewerExportRow {
    // 基本信息
    private Long userId;
    private String name;
    private String phone;
    private String title;
    private String institutionName;
    private String expertBackground;
    // 扩展档案
    private String gender;
    private String department;
    private String position;
    private String idNumber;
    private String idCardFront;
    private String idCardBack;
    private String bankName;
    private String bankCardNo;
    private String backgroundsJson;
    private String backgroundsOther;
    private String toolsJson;
    private String toolsOther;
    private String topicsJson;
    private String topicsOther;
    private String experienceJson;
    // 任务统计
    private Long taskScored;
    private Long taskDraft;
    private Long taskPending;
    private Long taskRecused;
    /** 已分配的决赛专场代码（逗号分隔，需传 competitionId 时才填充） */
    private String finalSessionCodes;
}
