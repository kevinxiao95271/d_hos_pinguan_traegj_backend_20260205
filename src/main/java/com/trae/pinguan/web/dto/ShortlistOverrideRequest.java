package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.ShortlistOverride;
import io.swagger.v3.oas.annotations.media.Schema;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
@Schema(description = "人工干预入围请求")
public class ShortlistOverrideRequest {

    @NotNull
    @Schema(description = "报名ID")
    private Long registrationId;

    @NotNull
    @Schema(description = "干预类型：INCLUDE=强制入围，EXCLUDE=强制淘汰")
    private ShortlistOverride override;

    @Schema(description = "干预说明（原因）")
    private String note;
}
