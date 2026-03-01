package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.RoleType;
import java.util.Optional;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface UserAccountRepository extends JpaRepository<UserAccount, Long>, JpaSpecificationExecutor<UserAccount> {
    @Query("SELECT u FROM UserAccount u LEFT JOIN FETCH u.institution WHERE u.phone = :phone")
    Optional<UserAccount> findByPhone(@Param("phone") String phone);
    List<UserAccount> findByRole(RoleType role);
    
    // 优化：使用JOIN FETCH一次性加载评委和关联的机构
    @Query("SELECT u FROM UserAccount u LEFT JOIN FETCH u.institution WHERE u.role = :role")
    List<UserAccount> findByRoleWithInstitution(@Param("role") RoleType role);
    
    // 统计用户数量
    @Query("SELECT COUNT(u) FROM UserAccount u WHERE " +
           "(:role IS NULL OR u.role = :role) AND " +
           "(:enabled IS NULL OR u.enabled = :enabled)")
    long countByRoleAndEnabled(@Param("role") RoleType role, @Param("enabled") Boolean enabled);
    
    // 更新启用状态
    @Modifying
    @Query("UPDATE UserAccount u SET u.enabled = :enabled WHERE u.id = :id")
    int updateEnabledStatus(@Param("id") Long id, @Param("enabled") Boolean enabled);
}
