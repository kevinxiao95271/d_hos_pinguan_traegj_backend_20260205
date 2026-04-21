package com.trae.pinguan.web.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class NoticeConfirmRequest {

    /**
     * 须知标识，如 BOOK / INTERVIEW，与前端 integrityNotices.js 保持一致。
     */
    @NotBlank(message = "noticeKey 不能为空")
    private String noticeKey;
}
