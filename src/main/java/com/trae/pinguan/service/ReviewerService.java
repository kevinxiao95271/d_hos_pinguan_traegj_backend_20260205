package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.repository.ReviewTaskRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.ReviewerListItem;
import com.trae.pinguan.web.dto.ReviewerUpsertRequest;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ReviewerService {
    private final UserAccountRepository userAccountRepository;
    private final InstitutionRepository institutionRepository;
    private final ReviewTaskRepository reviewTaskRepository;

    @Transactional(readOnly = true)
    public List<ReviewerListItem> list(Long institutionId,
                                       String reviewerGroupCode,
                                       String interviewGroupCode,
                                       String expertBackground) {
        // 优化：使用JOIN FETCH一次性加载所有关联数据，避免N+1问题
        List<UserAccount> reviewers = userAccountRepository.findByRoleWithInstitution(RoleType.REVIEWER);
        
        // 计算每个评委的负荷（已分配任务数）
        Map<Long, Integer> loadMap = new HashMap<>();
        for (UserAccount reviewer : reviewers) {
            int load = reviewTaskRepository.findByReviewerId(reviewer.getId()).size();
            loadMap.put(reviewer.getId(), load);
        }
        
        return reviewers.stream()
                .filter(user -> institutionId == null || (user.getInstitution() != null
                        && institutionId.equals(user.getInstitution().getId())))
                .filter(user -> reviewerGroupCode == null || reviewerGroupCode.equals(user.getReviewerGroupCode()))
                .filter(user -> interviewGroupCode == null || interviewGroupCode.equals(user.getInterviewGroupCode()))
                .filter(user -> expertBackground == null || expertBackground.equals(user.getExpertBackground()))
                .map(user -> new ReviewerListItem(
                        user.getId(),
                        user.getPhone(),
                        user.getName(),
                        user.getTitle(),
                        user.getInstitution() == null ? null : user.getInstitution().getId(),
                        user.getInstitution() == null ? null : user.getInstitution().getName(),
                        user.getReviewerGroupCode(),
                        user.getInterviewGroupCode(),
                        user.getExpertBackground(),
                        loadMap.getOrDefault(user.getId(), 0)
                ))
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public UserAccount get(Long id) {
        UserAccount user = userAccountRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("评委不存在"));
        if (user.getRole() != RoleType.REVIEWER) {
            throw new IllegalArgumentException("非评委账号");
        }
        return user;
    }

    @Transactional
    public UserAccount create(ReviewerUpsertRequest request) {
        userAccountRepository.findByPhone(request.getPhone()).ifPresent(item -> {
            throw new IllegalArgumentException("手机号已存在");
        });
        Institution institution = null;
        if (request.getInstitutionId() != null) {
            institution = institutionRepository.findById(request.getInstitutionId())
                    .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
        }
        UserAccount user = UserAccount.builder()
                .phone(request.getPhone())
                .name(request.getName())
                .title(request.getTitle())
                .role(RoleType.REVIEWER)
                .institution(institution)
                .reviewerGroupCode(request.getReviewerGroupCode())
                .interviewGroupCode(request.getInterviewGroupCode())
                .expertBackground(request.getExpertBackground())
                .createdAt(LocalDateTime.now())
                .build();
        return userAccountRepository.save(user);
    }

    @Transactional
    public UserAccount update(Long id, ReviewerUpsertRequest request) {
        UserAccount user = get(id);
        if (request.getPhone() != null && !request.getPhone().equals(user.getPhone())) {
            userAccountRepository.findByPhone(request.getPhone()).ifPresent(item -> {
                throw new IllegalArgumentException("手机号已存在");
            });
            user.setPhone(request.getPhone());
        }
        if (request.getName() != null) {
            user.setName(request.getName());
        }
        if (request.getTitle() != null) {
            user.setTitle(request.getTitle());
        }
        if (request.getInstitutionId() != null) {
            Institution institution = institutionRepository.findById(request.getInstitutionId())
                    .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
            user.setInstitution(institution);
        }
        if (request.getReviewerGroupCode() != null) {
            user.setReviewerGroupCode(request.getReviewerGroupCode());
        }
        if (request.getInterviewGroupCode() != null) {
            user.setInterviewGroupCode(request.getInterviewGroupCode());
        }
        if (request.getExpertBackground() != null) {
            user.setExpertBackground(request.getExpertBackground());
        }
        return userAccountRepository.save(user);
    }

    @Transactional
    public void delete(Long id) {
        UserAccount user = get(id);
        userAccountRepository.delete(user);
    }
}
