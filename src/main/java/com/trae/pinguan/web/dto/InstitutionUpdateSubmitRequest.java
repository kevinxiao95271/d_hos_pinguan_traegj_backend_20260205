package com.trae.pinguan.web.dto;

import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class InstitutionUpdateSubmitRequest {
    @NotNull
    private Long institutionId;
    @NotNull
    private Long submitterId;
    private String newName;
    private String newCode;
    private String newUscc;
}
