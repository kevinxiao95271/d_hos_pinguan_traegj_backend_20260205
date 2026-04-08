package com.trae.pinguan.domain.enums;

public enum ReviewStatus {
    PENDING,
    CONFIRMED,
    /** 草稿已保存，评分填写中但尚未正式提交 */
    DRAFT,
    SCORED,
    RETURNED,
    /** 评委主动申请规避该评审任务 */
    RECUSED
}
