package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.MemberRole;
import java.util.List;
import javax.validation.Valid;
import javax.validation.constraints.NotEmpty;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class MemberUpsertRequest {
    private Long registrationId;
    @Valid
    @NotEmpty(message = "成员列表不能为空")
    private List<MemberItem> members;  // 改为members，更符合前端习惯

    @Data
    public static class MemberItem {
        @NotNull(message = "角色不能为空")
        private MemberRole role;
        @javax.validation.constraints.NotBlank(message = "姓名不能为空")
        private String name;
        @javax.validation.constraints.NotBlank(message = "职称不能为空")
        private String title;
        private String department;  // 可选字段
    }
}
