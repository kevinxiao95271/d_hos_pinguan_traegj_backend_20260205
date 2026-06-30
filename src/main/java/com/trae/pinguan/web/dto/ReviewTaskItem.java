package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewTaskItem {
    private Long id;
    private Long registrationId;
    /** 项目编号（提交成功后生成的唯一序号） */
    private String projectName;
    private String institutionName;
    private String institutionLevel;
    private ReviewStage stage;
    private ReviewStatus status;
    private LocalDateTime createdAt;
    /** 当前保存的总分（草稿或已提交均返回；未填写时为 null） */
    private Double total;
    /** 规避原因code（RECUSED状态时有值） */
    private String recuseReasonCode;
    /** 规避原因说明（RECUSED状态且原因为OTHER时有值） */
    private String recuseReasonOther;
}
