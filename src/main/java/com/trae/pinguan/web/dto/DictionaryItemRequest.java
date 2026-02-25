package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.validation.constraints.NotBlank;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "字典项创建请求")
public class DictionaryItemRequest {
    
    @NotBlank(message = "字典类型不能为空")
    @Schema(description = "字典类型", example = "subject_type", required = true)
    private String type;
    
    @NotBlank(message = "字典代码不能为空")
    @Schema(description = "字典代码", example = "TYPE_01", required = true)
    private String code;
    
    @NotBlank(message = "显示标签不能为空")
    @Schema(description = "显示标签", example = "类型一", required = true)
    private String label;
    
    @Schema(description = "是否启用", example = "true")
    private Boolean active;
}
