package com.trae.pinguan.domain.enums;

import lombok.Getter;

@Getter
public enum SystemTemplateType {
    REGISTRATION_FORM("registration_form", "报名表模版"),
    RESULT_REPORT("result_report", "成果报告说明");
    
    private final String code;
    private final String label;
    
    SystemTemplateType(String code, String label) {
        this.code = code;
        this.label = label;
    }
    
    public static SystemTemplateType fromCode(String code) {
        for (SystemTemplateType type : values()) {
            if (type.code.equals(code)) {
                return type;
            }
        }
        throw new IllegalArgumentException("未知的模版类型: " + code);
    }
}
