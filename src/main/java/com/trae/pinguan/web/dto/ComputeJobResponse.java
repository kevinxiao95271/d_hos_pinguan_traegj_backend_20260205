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
@Schema(description = "算分任务状态")
public class ComputeJobResponse {

    @Schema(description = "任务ID，用于轮询状态")
    private String jobId;

    @Schema(description = "任务状态：RUNNING / SUCCESS / FAILED")
    private String status;

    @Schema(description = "写入快照条数（SUCCESS 时才有值）")
    private Integer snapshotCount;

    @Schema(description = "错误信息（FAILED 时才有值）")
    private String error;

    @Schema(description = "任务开始时间")
    private LocalDateTime startedAt;

    @Schema(description = "任务完成时间（RUNNING 时为 null）")
    private LocalDateTime finishedAt;
}
