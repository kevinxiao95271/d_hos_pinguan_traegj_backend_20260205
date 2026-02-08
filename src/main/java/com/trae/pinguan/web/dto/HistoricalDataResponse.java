package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 历史数据响应
 */
@Data
@Schema(description = "历史数据响应")
public class HistoricalDataResponse {
    
    @Schema(description = "ID")
    private Integer id;
    
    @Schema(description = "数据状态")
    private String dataStatus;
    
    @Schema(description = "录入人")
    private String inputPerson;
    
    @Schema(description = "录入日期")
    private String inputDate;
    
    @Schema(description = "年份")
    private String year;
    
    @Schema(description = "组名")
    private String groupName;
    
    @Schema(description = "项目编号")
    private String projectCode;
    
    @Schema(description = "竞赛组别")
    private String competitionGroup;
    
    @Schema(description = "项目名称")
    private String projectName;
    
    @Schema(description = "机构名称")
    private String institutionName;
    
    @Schema(description = "机构级别")
    private String institutionLevel;
    
    @Schema(description = "机构地址")
    private String institutionAddress;
    
    @Schema(description = "床位数")
    private String totalBeds;
    
    @Schema(description = "医院联系人姓名")
    private String hospitalContactName;
    
    @Schema(description = "医院联系人职称")
    private String hospitalContactTitle;
    
    @Schema(description = "医院联系人电话")
    private String hospitalContactPhone;
    
    @Schema(description = "医院联系人邮箱")
    private String hospitalContactEmail;
    
    @Schema(description = "项目负责人姓名")
    private String projectLeaderName;
    
    @Schema(description = "项目负责人职称")
    private String projectLeaderTitle;
    
    @Schema(description = "项目负责人电话")
    private String projectLeaderPhone;
    
    @Schema(description = "项目负责人邮箱")
    private String projectLeaderEmail;
    
    @Schema(description = "圈名")
    private String circleName;
}
