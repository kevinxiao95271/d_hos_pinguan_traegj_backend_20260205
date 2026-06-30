package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.CompetitionStage;
import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;
import lombok.Data;

@Data
@Schema(description = "赛事配置更新请求（时间窗口 + 阶段，字段均可选，仅更新传入的非 null 字段）")
public class CompetitionConfigRequest {

    @Schema(description = "赛事名称，唯一，传入则覆盖原名称")
    private String name;

    @Schema(description = "赛事阶段：REGISTER / BOOK_REVIEW / INTERVIEW / FINAL")
    private CompetitionStage stage;

    @Schema(description = "报名开始时间")
    private LocalDateTime registerStart;

    @Schema(description = "报名结束时间")
    private LocalDateTime registerEnd;

    @Schema(description = "书审开始时间")
    private LocalDateTime bookReviewStart;

    @Schema(description = "书审结束时间")
    private LocalDateTime bookReviewEnd;

    @Schema(description = "面谈开始时间")
    private LocalDateTime interviewStart;

    @Schema(description = "面谈结束时间")
    private LocalDateTime interviewEnd;

    @Schema(description = "决赛开始时间")
    private LocalDateTime finalStart;

    @Schema(description = "决赛结束时间")
    private LocalDateTime finalEnd;

    @Schema(description = "基层组分组前缀，如 A")
    private String basicGroupPrefix;

    @Schema(description = "综合组分组前缀，如 B")
    private String comprehensiveGroupPrefix;

    @Schema(description = "进阶组分组前缀，如 C")
    private String advancedGroupPrefix;
}
