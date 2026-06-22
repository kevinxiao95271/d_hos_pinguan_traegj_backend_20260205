package com.trae.pinguan.web;

import com.trae.pinguan.exception.DuplicateProjectNameException;
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
}
