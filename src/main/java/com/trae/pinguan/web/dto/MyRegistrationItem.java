package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.RegistrationStatus;
import java.time.LocalDateTime;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MyRegistrationItem {
    @Schema(description = "是否为草稿（true 时 id 为 draftId）")
    private Boolean draft;
    private Long id;
    private String projectName;
    private GroupType groupType;
    private String groupCode;
    private RegistrationStatus status;
    private LocalDateTime submittedAt;
    private LocalDateTime createdAt;
    
    // 机构信息
    private Long institutionId;
    private String institutionName;
    private String institutionLevel;
    
    // 赛事信息
    private Long competitionId;
    private String competitionName;
}
