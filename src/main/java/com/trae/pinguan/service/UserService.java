package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.LoginRequest;
import java.time.LocalDateTime;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserAccountRepository userAccountRepository;
    private final InstitutionRepository institutionRepository;

    @Transactional
    public UserAccount loginOrCreate(LoginRequest request) {
        UserAccount existing = userAccountRepository.findByPhone(request.getPhone()).orElse(null);
        Institution institution = null;
        if (request.getInstitutionId() != null) {
            institution = institutionRepository.findById(request.getInstitutionId())
                    .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
        }
        if (existing == null) {
            return userAccountRepository.save(UserAccount.builder()
                    .phone(request.getPhone())
                    .name(request.getName())
                    .title(request.getTitle())
                    .role(request.getRole())
                    .institution(institution)
                    .reviewerGroupCode(request.getReviewerGroupCode())
                    .interviewGroupCode(request.getInterviewGroupCode())
                    .expertBackground(request.getExpertBackground())
                    .createdAt(LocalDateTime.now())
                    .build());
        }
        if (request.getName() != null) {
            existing.setName(request.getName());
        }
        if (request.getTitle() != null) {
            existing.setTitle(request.getTitle());
        }
        if (request.getRole() != null) {
            existing.setRole(request.getRole());
        }
        if (institution != null) {
            existing.setInstitution(institution);
        }
        if (request.getReviewerGroupCode() != null) {
            existing.setReviewerGroupCode(request.getReviewerGroupCode());
        }
        if (request.getInterviewGroupCode() != null) {
            existing.setInterviewGroupCode(request.getInterviewGroupCode());
        }
        if (request.getExpertBackground() != null) {
            existing.setExpertBackground(request.getExpertBackground());
        }
        UserAccount saved = userAccountRepository.save(existing);
        // 强制加载institution以避免LazyInitializationException
        if (saved.getInstitution() != null) {
            saved.getInstitution().getName();
        }
        return saved;
    }
}
