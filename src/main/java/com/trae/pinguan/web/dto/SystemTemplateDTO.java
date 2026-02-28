package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "系统模版信息")
public class SystemTemplateDTO {
    @Schema(description = "模版ID")
    private Long id;
    
    @Schema(description = "模版类型", example = "registration_form")
    private String templateType;
    
    @Schema(description = "文件名")
    private String fileName;
    
    @Schema(description = "文件大小（字节）")
    private Long fileSize;
    
    @Schema(description = "版本号")
    private Integer version;
    
    @Schema(description = "是否激活")
    private Boolean isActive;
    
    @Schema(description = "上传人")
    private String uploadedBy;
    
    @Schema(description = "上传时间")
    private LocalDateTime uploadedAt;
    
    @Schema(description = "描述")
    private String description;
}
