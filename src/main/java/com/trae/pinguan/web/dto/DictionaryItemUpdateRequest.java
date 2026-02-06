package com.trae.pinguan.web.dto;

import lombok.Data;

@Data
public class DictionaryItemUpdateRequest {
    private String type;
    private String code;
    private String label;
    private Boolean active;
}
