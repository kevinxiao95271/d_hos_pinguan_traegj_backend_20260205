package com.trae.pinguan.web.dto;

import java.time.LocalDateTime;
import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CompetitionCreateRequest {
    @NotBlank
    private String name;
    private LocalDateTime registerStart;
    private LocalDateTime registerEnd;
    private LocalDateTime bookReviewStart;
    private LocalDateTime bookReviewEnd;
    private LocalDateTime interviewStart;
    private LocalDateTime interviewEnd;
    private LocalDateTime finalStart;
    private LocalDateTime finalEnd;

    /** 基层组分组前缀，不填默认 A */
    private String basicGroupPrefix;
    /** 综合组分组前缀，不填默认 B */
    private String comprehensiveGroupPrefix;
    /** 进阶组分组前缀，不填默认 C */
    private String advancedGroupPrefix;
}
