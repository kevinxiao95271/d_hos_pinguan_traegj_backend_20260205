package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
public class RegistrationUpdateRequest {
    @Size(max = 100)
    private String projectName;
    private GroupType groupType;
    private Long institutionId;
}
