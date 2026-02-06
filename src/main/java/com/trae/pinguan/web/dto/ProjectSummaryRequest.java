package com.trae.pinguan.web.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class ProjectSummaryRequest {
    private Long registrationId;
    @NotBlank
    private String theme;
    @NotBlank
    private String plan;
    @NotBlank
    private String problem;
    @NotBlank
    private String action;
    @NotBlank
    private String success;
    @NotBlank
    private String discussion;
}
