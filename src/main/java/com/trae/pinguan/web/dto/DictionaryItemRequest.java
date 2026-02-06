package com.trae.pinguan.web.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class DictionaryItemRequest {
    @NotBlank
    private String type;
    @NotBlank
    private String code;
    @NotBlank
    private String label;
    @NotNull
    private Boolean active;
}
