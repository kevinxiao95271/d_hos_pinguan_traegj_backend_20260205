package com.trae.pinguan.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

@Service
@Slf4j
public class SmsService {
    
    // 验证码存储（生产环境建议使用Redis）
    private final ConcurrentHashMap<String, SmsCode> codeStore = new ConcurrentHashMap<>();
    
    @Value("${sms.enabled:false}")
    private boolean smsEnabled;
    
    @Value("${sms.mock:true}")
    private boolean mockMode;
    
    /**
     * 发送验证码
     */
    public boolean sendVerificationCode(String phone, SmsCodeType type) {
        // 1. 验证手机号格式
        if (!isValidPhone(phone)) {
            throw new IllegalArgumentException("手机号格式不正确");
        }
        
        // 2. 检查发送频率（防刷）
        if (hasSentRecently(phone)) {
            throw new IllegalArgumentException("验证码已发送，请60秒后再试");
        }
        
        // 3. 生成6位数字验证码
        String code = generateCode();
        
        // 4. 发送短信
        boolean success;
        if (mockMode || !smsEnabled) {
            // 模拟模式：直接返回成功，验证码打印到日志
            log.info("【模拟短信】发送验证码到 {}: {}", phone, code);
            success = true;
        } else {
            // 真实模式：调用短信服务商API
            success = sendSmsViaSmsProvider(phone, code, type);
        }
        
        if (success) {
            // 5. 存储验证码（5分钟有效期）
            SmsCode smsCode = new SmsCode(code, System.currentTimeMillis() + TimeUnit.MINUTES.toMillis(5));
            codeStore.put(phone, smsCode);
            log.info("验证码已发送到 {}, 有效期5分钟", phone);
        }
        
        return success;
    }
    
    /**
     * 验证验证码
     */
    public boolean verifyCode(String phone, String code) {
        SmsCode stored = codeStore.get(phone);
        
        if (stored == null) {
            log.warn("验证码不存在: {}", phone);
            return false;
        }
        
        // 检查是否过期
        if (System.currentTimeMillis() > stored.getExpireTime()) {
            codeStore.remove(phone);
            log.warn("验证码已过期: {}", phone);
            return false;
        }
        
        // 验证码比对
        boolean matches = stored.getCode().equals(code);
        
        if (matches) {
            // 验证成功后立即删除（一次性）
            codeStore.remove(phone);
            log.info("验证码验证成功: {}", phone);
        } else {
            log.warn("验证码错误: {}, 输入: {}, 实际: {}", phone, code, stored.getCode());
        }
        
        return matches;
    }
    
    /**
     * 调用短信服务商API发送短信
     * 这里需要根据实际选择的服务商进行实现
     */
    private boolean sendSmsViaSmsProvider(String phone, String code, SmsCodeType type) {
        try {
            // TODO: 集成实际的短信服务商
            // 示例：阿里云短信、腾讯云短信等
            
            // 阿里云示例（需要添加aliyun-java-sdk依赖）:
            // DefaultProfile profile = DefaultProfile.getProfile("cn-hangzhou", accessKeyId, accessKeySecret);
            // IAcsClient client = new DefaultAcsClient(profile);
            // SendSmsRequest request = new SendSmsRequest();
            // request.setPhoneNumbers(phone);
            // request.setSignName("品管大赛");
            // request.setTemplateCode("SMS_123456789");
            // request.setTemplateParam("{\"code\":\"" + code + "\"}");
            // SendSmsResponse response = client.getAcsResponse(request);
            // return "OK".equals(response.getCode());
            
            log.info("调用短信服务商API发送验证码到 {}: {}", phone, code);
            return true;
            
        } catch (Exception e) {
            log.error("发送短信失败: {}", e.getMessage(), e);
            return false;
        }
    }
    
    /**
     * 生成6位随机数字验证码
     */
    private String generateCode() {
        Random random = new Random();
        return String.format("%06d", random.nextInt(1000000));
    }
    
    /**
     * 验证手机号格式
     */
    private boolean isValidPhone(String phone) {
        return phone != null && phone.matches("^1[3-9]\\d{9}$");
    }
    
    /**
     * 检查是否在60秒内已发送过
     */
    private boolean hasSentRecently(String phone) {
        SmsCode stored = codeStore.get(phone);
        if (stored == null) {
            return false;
        }
        
        // 检查距离上次发送是否超过60秒
        long timeSinceSent = System.currentTimeMillis() - (stored.getExpireTime() - TimeUnit.MINUTES.toMillis(5));
        return timeSinceSent < TimeUnit.SECONDS.toMillis(60);
    }
    
    /**
     * 清理过期验证码（定时任务调用）
     */
    public void cleanExpiredCodes() {
        long now = System.currentTimeMillis();
        codeStore.entrySet().removeIf(entry -> entry.getValue().getExpireTime() < now);
        log.debug("清理过期验证码，剩余: {}", codeStore.size());
    }
    
    /**
     * 验证码类型
     */
    public enum SmsCodeType {
        REGISTER("注册"),
        LOGIN("登录"),
        RESET_PASSWORD("重置密码"),
        CHANGE_PHONE("更换手机号");
        
        private final String description;
        
        SmsCodeType(String description) {
            this.description = description;
        }
        
        public String getDescription() {
            return description;
        }
    }
    
    /**
     * 验证码存储对象
     */
    private static class SmsCode {
        private final String code;
        private final long expireTime;
        
        public SmsCode(String code, long expireTime) {
            this.code = code;
            this.expireTime = expireTime;
        }
        
        public String getCode() {
            return code;
        }
        
        public long getExpireTime() {
            return expireTime;
        }
    }
}
