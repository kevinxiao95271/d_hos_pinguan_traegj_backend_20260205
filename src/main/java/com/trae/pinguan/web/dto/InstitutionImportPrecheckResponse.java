package com.trae.pinguan.web.dto;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class InstitutionImportPrecheckResponse {
    private List<DuplicateItem> duplicates;
    private Integer willCreateCount;
    private Integer totalCount;

    @Data
    @AllArgsConstructor
    public static class DuplicateItem {
        private String name;
        private String uscc;
        private Boolean nameDuplicate;
        private Boolean usccDuplicate;
    }
}
