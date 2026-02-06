package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class GroupedRegistrationResponse {
    @Schema(example = "M1")
    private String groupCode;
    private List<GroupedRegistrationItem> items;
}
