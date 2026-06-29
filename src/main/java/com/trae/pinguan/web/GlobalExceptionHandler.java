package com.trae.pinguan.web;

import com.trae.pinguan.exception.DuplicateProjectNameException;
import com.trae.pinguan.exception.PrefixLockedByGroupingException;
import com.trae.pinguan.web.dto.ApiResponse;
import java.util.List;
import java.util.Map;
import javax.validation.ConstraintViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(DuplicateProjectNameException.class)
    @ResponseStatus(HttpStatus.CONFLICT)
    public ApiResponse<List<Map<String, Object>>> handleDuplicateProjectName(
            DuplicateProjectNameException ex) {
        return ApiResponse.failWithCode(
                DuplicateProjectNameException.ERROR_CODE,
                ex.getMessage(),
                ex.getMatches());
    }

    @ExceptionHandler(PrefixLockedByGroupingException.class)
    @ResponseStatus(HttpStatus.UNPROCESSABLE_ENTITY)
    public ApiResponse<Void> handlePrefixLocked(PrefixLockedByGroupingException ex) {
        return ApiResponse.failWithCode(
                PrefixLockedByGroupingException.ERROR_CODE,
                ex.getMessage(),
                null);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleIllegalArgument(IllegalArgumentException ex) {
        return ApiResponse.fail(ex.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleValidation(MethodArgumentNotValidException ex) {
        return ApiResponse.fail("参数校验失败");
    }

    @ExceptionHandler(ConstraintViolationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleConstraint(ConstraintViolationException ex) {
        return ApiResponse.fail("参数校验失败");
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResponse<String> handleGeneral(Exception ex) {
        StringBuilder msg = new StringBuilder(ex.getClass().getSimpleName())
                .append(": ").append(ex.getMessage());
        // 只取第一个属于我们代码的栈帧，精确定位 NPE 位置
        for (StackTraceElement ste : ex.getStackTrace()) {
            if (ste.getClassName().startsWith("com.trae.pinguan")) {
                msg.append(" @ ").append(ste.getClassName())
                   .append(".").append(ste.getMethodName())
                   .append("(").append(ste.getFileName())
                   .append(":").append(ste.getLineNumber()).append(")");
                break;
            }
        }
        if (ex.getCause() != null) {
            msg.append(" | cause: ").append(ex.getCause().getClass().getSimpleName());
        }
        return ApiResponse.fail(msg.toString());
    }
}
