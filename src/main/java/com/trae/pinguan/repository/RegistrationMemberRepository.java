package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.RegistrationMember;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RegistrationMemberRepository extends JpaRepository<RegistrationMember, Long> {
    List<RegistrationMember> findByRegistrationId(Long registrationId);
}
