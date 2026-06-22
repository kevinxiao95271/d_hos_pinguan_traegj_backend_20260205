package com.trae.pinguan.exception;

import java.util.List;
import java.util.Map;

/**
 * 提交报名时，项目名称与同单位已有项目相似度 ≥ 80% 时抛出。
 * errorCode = DUPLICATE_PROJECT_NAME，携带命中列表供前端展示并引导修改。
 */
public class DuplicateProjectNameException extends RuntimeException {

    public static final String ERROR_CODE = "DUPLICATE_PROJECT_NAME";

    private final List<Map<String, Object>> matches;

    public DuplicateProjectNameException(List<Map<String, Object>> matches) {
        super("存在高度相似的项目名称，请修改后重新提交");
        this.matches = matches;
    }

    public List<Map<String, Object>> getMatches() {
        return matches;
    }
}
