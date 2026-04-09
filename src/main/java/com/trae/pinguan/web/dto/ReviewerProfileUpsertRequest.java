package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
@Schema(description = "评审专家扩展档案更新请求")
public class ReviewerProfileUpsertRequest {
    @Schema(description = "性别：MALE/FEMALE/UNKNOWN")
    @Size(max = 8, message = "性别长度不能超过8")
    private String gender;

    @Schema(description = "职务")
    @Size(max = 64, message = "职务长度不能超过64")
    private String position;

    @Schema(description = "科室")
    @Size(max = 64, message = "科室长度不能超过64")
    private String department;

    @Schema(description = "身份证号")
    @Size(max = 64, message = "身份证号长度不能超过64")
    private String idNumber;

    @Schema(description = "身份证号脱敏")
    @Size(max = 32, message = "身份证号脱敏长度不能超过32")
    private String idNumberMasked;

    @Schema(description = "身份证正面图片URL")
    @Size(max = 500, message = "身份证正面图片URL长度不能超过500")
    private String idCardFrontUrl;

    @Schema(description = "身份证反面图片URL")
    @Size(max = 500, message = "身份证反面图片URL长度不能超过500")
    private String idCardBackUrl;

    @Schema(description = "开户银行")
    @Size(max = 128, message = "开户银行长度不能超过128")
    private String bankName;

    @Schema(description = "银行卡号")
    @Size(max = 128, message = "银行卡号长度不能超过128")
    private String bankCardNo;

    @Schema(description = "银行卡号脱敏")
    @Size(max = 32, message = "银行卡号脱敏长度不能超过32")
    private String bankCardNoMasked;

    @Schema(description = "专业背景多选JSON数组，如 [\"MEDICAL\",\"NURSING\"]")
    private String backgroundsJson;

    @Schema(description = "专业背景-其他，文字说明")
    @Size(max = 255, message = "专业背景其他说明不能超过255字")
    private String backgroundsOther;

    @Schema(description = "熟悉工具多选JSON数组，如 [\"PDCA\",\"QFD\"]")
    private String toolsJson;

    @Schema(description = "熟悉工具-其他，文字说明")
    @Size(max = 255, message = "熟悉工具其他说明不能超过255字")
    private String toolsOther;

    @Schema(description = "擅长主题多选JSON数组，如 [\"PATIENT_CARE\",\"MEDICAL_QUALITY_SAFETY\"]")
    private String topicsJson;

    @Schema(description = "擅长主题-其他，文字说明")
    @Size(max = 255, message = "擅长主题其他说明不能超过255字")
    private String topicsOther;

    @Schema(description = "品管相关经验，多选 JSON 数组，如 [\"PROJECT_LEADER\",\"CITY_JUDGE\"]。" +
            "可选值：PROJECT_LEADER（担任过品管项目负责人）、COACHED_PROJECT（辅导过品管参赛项目）、" +
            "UNIT_JUDGE（单位内品管大赛评委）、CITY_JUDGE（市/区/县级品管大赛评委）、" +
            "PROVINCE_JUDGE（省级及以上品管大赛评委）")
    private String experienceJson;

    @Schema(description = "职称，单选：初级 / 中级 / 副高 / 正高（更新 user_accounts.title）")
    @Size(max = 64, message = "职称长度不能超过64")
    private String title;
}
