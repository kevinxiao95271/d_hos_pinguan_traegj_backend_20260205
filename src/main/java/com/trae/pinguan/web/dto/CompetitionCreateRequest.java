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
}
