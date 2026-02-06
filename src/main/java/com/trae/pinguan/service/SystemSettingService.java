package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.SystemSetting;
import com.trae.pinguan.repository.SystemSettingRepository;
import com.trae.pinguan.web.dto.SystemSettingRequest;
import java.time.LocalDateTime;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class SystemSettingService {
    private final SystemSettingRepository systemSettingRepository;

    public SystemSetting get(String key) {
        return systemSettingRepository.findBySettingKey(key)
                .orElseThrow(() -> new IllegalArgumentException("配置不存在"));
    }

    @Transactional
    public SystemSetting upsert(SystemSettingRequest request) {
        SystemSetting setting = systemSettingRepository.findBySettingKey(request.getKey())
                .orElse(SystemSetting.builder().settingKey(request.getKey()).build());
        setting.setSettingValue(request.getValue());
        setting.setUpdatedAt(LocalDateTime.now());
        return systemSettingRepository.save(setting);
    }
}
