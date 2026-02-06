package com.trae.pinguan.web.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class SystemSettingRequest {
    @NotBlank
    private String key;
    @NotBlank
    private String value;
}
