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

    @Schema(description = "熟悉工具多选JSON数组，如 [\"PDCA\",\"QFD\"]")
    private String toolsJson;

    @Schema(description = "擅长主题多选JSON数组，如 [\"PATIENT_CARE\",\"MEDICAL_QUALITY_SAFETY\"]")
    private String topicsJson;
}
