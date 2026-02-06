package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.RoleType;
import java.util.Optional;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface UserAccountRepository extends JpaRepository<UserAccount, Long> {
    Optional<UserAccount> findByPhone(String phone);
    List<UserAccount> findByRole(RoleType role);
    
    // 优化：使用JOIN FETCH一次性加载评委和关联的机构
    @Query("SELECT u FROM UserAccount u LEFT JOIN FETCH u.institution WHERE u.role = :role")
    List<UserAccount> findByRoleWithInstitution(@Param("role") RoleType role);
}
