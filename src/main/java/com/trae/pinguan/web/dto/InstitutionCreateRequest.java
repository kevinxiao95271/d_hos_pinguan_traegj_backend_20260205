package com.trae.pinguan.web.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class InstitutionCreateRequest {
    @NotBlank
    private String name;
    @NotBlank
    private String code;
    @NotBlank
    private String uscc;
    private String region;
}
