package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.SystemSetting;
import java.util.Optional;
import javax.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface SystemSettingRepository extends JpaRepository<SystemSetting, Long> {
    Optional<SystemSetting> findBySettingKey(String settingKey);

    /** SELECT ... FOR UPDATE：用于序列号自增，防止并发重复 */
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT s FROM SystemSetting s WHERE s.settingKey = :key")
    Optional<SystemSetting> findBySettingKeyForUpdate(@Param("key") String key);
}
