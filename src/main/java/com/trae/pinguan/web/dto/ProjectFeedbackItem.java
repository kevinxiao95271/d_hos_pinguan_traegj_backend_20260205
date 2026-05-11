package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.ReviewStage;
import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProjectFeedbackItem {
    @Schema(example = "101")
    private Long registrationId;
    @Schema(example = "项目A")
    private String projectName;
    @Schema(example = "某医院")
    private String institutionName;
    @Schema(example = "BASIC")
    private GroupType groupType;
    @Schema(example = "A1")
    private String groupCode;
    @Schema(example = "BOOK")
    private ReviewStage stage;
    @Schema(description = "评委原始亮点汇总")
    private String sourceHighlight;
    @Schema(description = "评委原始不足汇总")
    private String sourceWeakness;
    @Schema(description = "组委会编辑后的亮点")
    private String editedHighlight;
    @Schema(description = "组委会编辑后的不足")
    private String editedWeakness;
    @Schema(description = "最终展示给参赛者的亮点")
    private String finalHighlight;
    @Schema(description = "最终展示给参赛者的不足")
    private String finalWeakness;
    private boolean published;
    private LocalDateTime updatedAt;
    private LocalDateTime publishedAt;
}
