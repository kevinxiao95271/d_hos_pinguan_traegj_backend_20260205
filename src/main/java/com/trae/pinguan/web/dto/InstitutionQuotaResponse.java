package com.trae.pinguan.web.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InstitutionQuotaResponse {
    private Long institutionId;
    private String institutionName;
    private Long competitionId;
    private String competitionName;
    private Integer currentCount;      // 当前已报名数量
    private Integer maxCount;          // 最大允许报名数量
    private Integer remainingCount;    // 剩余可报名数量
    private Boolean canRegister;       // 是否还可以报名
}
