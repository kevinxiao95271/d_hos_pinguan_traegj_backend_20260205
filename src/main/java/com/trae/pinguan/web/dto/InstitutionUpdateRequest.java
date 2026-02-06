package com.trae.pinguan.web.dto;

import lombok.Data;

@Data
public class InstitutionUpdateRequest {
    private String name;
    private String code;
    private String uscc;
    private String region;
}
