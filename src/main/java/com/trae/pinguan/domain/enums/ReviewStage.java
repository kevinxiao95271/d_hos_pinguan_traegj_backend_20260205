package com.trae.pinguan.domain.enums;

public enum ReviewStage {
    BOOK,
    INTERVIEW,
    /** 纯面谈系数排名（进阶组不合并书审分，与 INTERVIEW 快照完全隔离） */
    INTERVIEW_ONLY,
    FINAL
}
