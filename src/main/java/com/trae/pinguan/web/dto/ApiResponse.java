package com.trae.pinguan.web.dto;

public class ApiResponse<T> {
    private boolean success;
    private T data;
    private String message;
    private String errorCode;

    public ApiResponse() {}

    public ApiResponse(boolean success, T data, String message, String errorCode) {
        this.success = success;
        this.data = data;
        this.message = message;
        this.errorCode = errorCode;
    }

    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    public T getData() { return data; }
    public void setData(T data) { this.data = data; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public String getErrorCode() { return errorCode; }
    public void setErrorCode(String errorCode) { this.errorCode = errorCode; }

    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<T>(true, data, null, null);
    }

    public static <T> ApiResponse<T> fail(String message) {
        return new ApiResponse<T>(false, null, message, null);
    }

    public static <T> ApiResponse<T> failWithCode(String errorCode, String message, T data) {
        return new ApiResponse<T>(false, data, message, errorCode);
    }
}
