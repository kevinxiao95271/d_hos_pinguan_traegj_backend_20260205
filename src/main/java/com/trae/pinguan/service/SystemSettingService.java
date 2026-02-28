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
    
    private static final String KEY_CURRENT_COMPETITION = "currentCompetitionId";

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
    
    /**
     * 获取当前活跃赛事ID（全局唯一）
     */
    public Long getCurrentCompetitionId() {
        return systemSettingRepository.findBySettingKey(KEY_CURRENT_COMPETITION)
                .map(setting -> Long.parseLong(setting.getSettingValue()))
                .orElse(null);
    }
    
    /**
     * 设置当前活跃赛事ID
     */
    @Transactional
    public void setCurrentCompetitionId(Long competitionId) {
        SystemSetting setting = systemSettingRepository.findBySettingKey(KEY_CURRENT_COMPETITION)
                .orElse(SystemSetting.builder().settingKey(KEY_CURRENT_COMPETITION).build());
        setting.setSettingValue(String.valueOf(competitionId));
        setting.setUpdatedAt(LocalDateTime.now());
        systemSettingRepository.save(setting);
    }
}
