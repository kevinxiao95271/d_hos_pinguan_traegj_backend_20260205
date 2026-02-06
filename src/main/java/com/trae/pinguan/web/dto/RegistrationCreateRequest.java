package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
public class RegistrationCreateRequest {
    @NotNull
    private Long competitionId;
    @NotNull
    private Long institutionId;
    // applicantId从token自动获取，前端不需要传
    private Long applicantId;
    @NotBlank
    @Size(max = 100)
    private String projectName;
    @NotNull
    private GroupType groupType;
}
