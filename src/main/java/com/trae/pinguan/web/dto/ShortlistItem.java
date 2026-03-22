package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ShortlistOverride;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ShortlistItem {
    private Integer irank;
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private GroupType groupType;
    private String groupCode;
    private ReviewStage stage;

    private Double rawAvg;
    private Double groupAvg;
    private Double overallAvg;
    private Double coefficient;
    private Double adjustedScore;

    private LocalDateTime calculatedAt;

    /** 是否在入围线内（按配置的比例/名额计算，不含人工干预） */
    private Boolean withinLine;

    /** 最终入围结果（综合 withinLine + override） */
    private Boolean shortlisted;

    /** 人工干预类型（null=无干预，INCLUDE=强制入围，EXCLUDE=强制淘汰） */
    private ShortlistOverride shortlistOverride;

    /** 人工干预说明 */
    private String shortlistNote;
}
