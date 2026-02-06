package com.trae.pinguan.web.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ReviewerUpsertRequest {
    @NotBlank
    private String phone;
    @NotBlank
    private String name;
    private String title;
    private Long institutionId;
    private String reviewerGroupCode;
    private String interviewGroupCode;
    private String expertBackground;
}
