package com.trae.pinguan.web.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class DataSourceSwitchRequest {
    @NotBlank
    private String target;
}
