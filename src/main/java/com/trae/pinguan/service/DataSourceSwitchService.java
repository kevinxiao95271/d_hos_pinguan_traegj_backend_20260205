package com.trae.pinguan.service;

import com.trae.pinguan.config.DataSourceContext;
import com.trae.pinguan.domain.entity.SystemSetting;
import com.trae.pinguan.repository.SystemSettingRepository;
import java.time.LocalDateTime;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class DataSourceSwitchService {
    private final SystemSettingRepository systemSettingRepository;

    public String current() {
        return DataSourceContext.getCurrent();
    }

    @Transactional
    public String switchTo(String target) {
        if (!"ds1".equals(target) && !"ds2".equals(target) && !"ds3".equals(target)) {
            throw new IllegalArgumentException("数据源不存在");
        }
        DataSourceContext.setCurrent(target);
        SystemSetting setting = systemSettingRepository.findBySettingKey("activeDataSource")
                .orElse(SystemSetting.builder().settingKey("activeDataSource").build());
        setting.setSettingValue(target);
        setting.setUpdatedAt(LocalDateTime.now());
        systemSettingRepository.save(setting);
        return target;
    }
}
