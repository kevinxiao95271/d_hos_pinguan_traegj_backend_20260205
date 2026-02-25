package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "字典项更新请求")
public class DictionaryItemUpdateRequest {
    
    @Schema(description = "显示标签", example = "更新后的标签")
    private String label;
    
    @Schema(description = "是否启用", example = "true")
    private Boolean active;
}
