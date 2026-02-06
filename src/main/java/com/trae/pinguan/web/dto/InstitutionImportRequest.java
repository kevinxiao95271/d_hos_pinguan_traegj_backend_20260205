package com.trae.pinguan.web.dto;

import java.util.List;
import javax.validation.constraints.NotEmpty;
import lombok.Data;

@Data
public class InstitutionImportRequest {
    @NotEmpty
    private List<InstitutionItem> items;

    @Data
    public static class InstitutionItem {
        private String name;
        private String code;
        private String uscc;
        private String region;
    }
}
