package com.trae.pinguan.domain.enums;

public enum CompetitionStatus {
    /** 草稿：刚创建，尚未对外开放，可删除、可修改 */
    DRAFT,
    /** 激活：对外开放，同年唯一，有报名记录后不可撤回 */
    ACTIVE
}
