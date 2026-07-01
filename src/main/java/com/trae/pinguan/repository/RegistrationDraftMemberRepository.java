package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.RegistrationDraftMember;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RegistrationDraftMemberRepository extends JpaRepository<RegistrationDraftMember, Long> {
    List<RegistrationDraftMember> findByDraftId(Long draftId);
    void deleteByDraftId(Long draftId);
}
