package com.trae.pinguan.web.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;
import javax.validation.Valid;
import javax.validation.constraints.NotEmpty;
import javax.validation.constraints.Size;
import lombok.Data;

@Data
public class ProjectFeedbackBatchUpdateRequest {

    @NotEmpty(message = "items 不能为空")
    @Size(max = 200, message = "单次批量保存最多 200 条")
    @Valid
    @Schema(description = "待保存的意见列表，最多 200 条")
    private List<Item> items;

    @Data
    public static class Item {
        @Schema(description = "报名 ID", example = "101", required = true)
        private Long registrationId;

        @Size(max = 5000, message = "亮点汇总不能超过 5000 字")
        @Schema(description = "组委会编辑后的亮点")
        private String highlight;

        @Size(max = 5000, message = "不足汇总不能超过 5000 字")
        @Schema(description = "组委会编辑后的不足")
        private String weakness;
    }
}
