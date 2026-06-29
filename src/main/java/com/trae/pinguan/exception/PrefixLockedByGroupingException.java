package com.trae.pinguan.exception;

/**
 * 赛事分组前缀已锁定：该赛事下存在已分组记录，不允许再修改前缀配置。
 * errorCode = PREFIX_LOCKED_BY_GROUPING
 */
public class PrefixLockedByGroupingException extends RuntimeException {

    public static final String ERROR_CODE = "PREFIX_LOCKED_BY_GROUPING";

    public PrefixLockedByGroupingException(Long competitionId) {
        super("赛事 " + competitionId + " 已存在分组记录，前缀配置已锁定，不可修改。" +
              "如需变更前缀，请先清除所有分组数据。");
    }
}
