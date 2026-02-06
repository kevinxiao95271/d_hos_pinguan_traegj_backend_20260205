package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class ActivityInfoRequest {
    private Long registrationId;
    // 主题
    @NotBlank(message = "主题不能为空")
    @Schema(example = "提高门诊预约效率")
    private String theme;
    // 关键词
    @NotBlank(message = "关键词不能为空")
    @Schema(example = "门诊,预约,效率")
    private String keywords;
    // 选题类型（可选值较多，建议从字典表获取）
    @NotBlank(message = "选题类型不能为空")
    @Schema(example = "subject_type_1", description = "选题类型代码，如：subject_type_1, subject_type_2等")
    private String subjectTypeCode;
    @Schema(example = "其他选题类型说明")
    private String subjectTypeOther;
    // 方法
    @NotBlank(message = "方法不能为空")
    @Schema(example = "PDCA", description = "方法代码，如：PDCA, DMAIC等")
    private String methodCode;
    @Schema(example = "其他方法说明")
    private String methodOther;
    // 改善经验
    @NotBlank(message = "改善经验不能为空")
    @Schema(example = "experience_1", description = "改善经验代码")
    private String experienceImproveCode;
    @Schema(example = "其他改善经验说明")
    private String experienceImproveOther;
    // 质量主题
    @NotBlank(message = "质量主题不能为空")
    @Schema(example = "quality_topic_1", description = "质量主题代码")
    private String qualityTopicCode;
    @Schema(example = "其他质量主题说明")
    private String qualityTopicOther;
    // 平均工作年限
    @NotNull(message = "平均工作年限不能为空")
    @Schema(example = "6", description = "团队成员平均工作年限（年）")
    private Integer avgWorkYears;
    // 平均年龄
    @NotNull(message = "平均年龄不能为空")
    @Schema(example = "32", description = "团队成员平均年龄（岁）")
    private Integer avgAge;
    // 是否跨部门
    @NotNull(message = "是否跨部门不能为空")
    @Schema(example = "false", description = "是否跨部门团队")
    private Boolean crossDepartment;
}
