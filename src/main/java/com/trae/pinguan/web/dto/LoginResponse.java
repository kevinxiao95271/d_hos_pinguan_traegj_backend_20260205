package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.enums.RoleType;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class LoginResponse {
    private Long id;
    private String phone;
    private String name;
    private String title;
    private RoleType role;
    private Long institutionId;
    private String institutionName;
    private String institutionCode;
    private String institutionUscc;
    private String expertBackground;
    private String token;
    private Long currentCompetitionId;
    private String currentCompetitionName;
    /** 兼容旧前端：是否已确认过诚信须知（true=已确认，false/null=未确认） */
    private Boolean noticeConfirmed;
    /**
     * 新字段：尚未确认的须知 key 列表，按前端弹窗顺序排列（如 ["BOOK", "INTERVIEW"]）。
     * 非 REVIEWER 角色返回 null；REVIEWER 全部已确认时返回空数组 []。
     * 新版前端以此字段为准，旧版前端忽略此字段不受影响。
     */
    private List<String> pendingIntegrityNoticeKeys;
}
