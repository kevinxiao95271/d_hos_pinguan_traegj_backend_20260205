package com.trae.pinguan.service;

import com.trae.pinguan.config.MinioProperties;
import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.domain.entity.ReviewerInstitutionChange;
import com.trae.pinguan.domain.entity.ReviewerProfile;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.repository.ReviewerInstitutionChangeRepository;
import com.trae.pinguan.repository.ReviewerProfileRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.ChangeInstitutionRequest;
import com.trae.pinguan.web.dto.ReviewerListItem;
import com.trae.pinguan.web.dto.ReviewerProfileDto;
import com.trae.pinguan.web.dto.ReviewerProfileUpsertRequest;
import com.trae.pinguan.web.dto.ReviewerUpsertRequest;
import java.io.InputStream;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;

@Service
@RequiredArgsConstructor
public class ReviewerService {
    private final UserAccountRepository userAccountRepository;
    private final InstitutionRepository institutionRepository;
    private final ReviewerProfileRepository reviewerProfileRepository;
    private final ReviewerInstitutionChangeRepository reviewerInstitutionChangeRepository;
    private final FileStorageService fileStorageService;
    private final MinioProperties minioProperties;

    @Transactional(readOnly = true)
    public List<ReviewerListItem> list(Long institutionId,
                                       String reviewerGroupCode,
                                       String interviewGroupCode,
                                       String expertBackground) {
        // 优化：使用JOIN FETCH一次性加载所有关联数据，避免N+1问题
        List<UserAccount> reviewers = userAccountRepository.findByRoleWithInstitution(RoleType.REVIEWER);
        return reviewers.stream()
                .filter(user -> Boolean.TRUE.equals(user.getEnabled()))
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
                        user.getExpertBackground()
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

    @Transactional(readOnly = true)
    public ReviewerProfileDto getProfile(Long reviewerId) {
        UserAccount user = get(reviewerId);
        ReviewerProfile profile = reviewerProfileRepository.findById(reviewerId)
                .orElse(null);
        if (profile == null) {
            return ReviewerProfileDto.builder()
                    .userId(reviewerId)
                    .name(user.getName())
                    .phone(user.getPhone())
                    .title(user.getTitle())
                    .institutionName(user.getInstitution() == null ? null : user.getInstitution().getName())
                    .build();
        }
        return toDto(user, profile);
    }

    @Transactional
    public ReviewerProfileDto upsertProfile(Long reviewerId, ReviewerProfileUpsertRequest request) {
        UserAccount user = get(reviewerId);
        LocalDateTime now = LocalDateTime.now();
        ReviewerProfile profile = reviewerProfileRepository.findById(reviewerId)
                .orElse(ReviewerProfile.builder()
                        .userId(reviewerId)
                        .createdAt(now)
                        .build());

        profile.setGender(request.getGender());
        profile.setPosition(request.getPosition());
        profile.setIdNumber(request.getIdNumber());
        profile.setIdNumberMasked(request.getIdNumberMasked());
        profile.setIdCardFrontUrl(request.getIdCardFrontUrl());
        profile.setIdCardBackUrl(request.getIdCardBackUrl());
        profile.setDepartment(request.getDepartment());
        profile.setBankName(request.getBankName());
        profile.setBankCardNo(request.getBankCardNo());
        profile.setBankCardNoMasked(request.getBankCardNoMasked());
        profile.setBackgroundsJson(request.getBackgroundsJson());
        profile.setBackgroundsOther(request.getBackgroundsOther());
        profile.setToolsJson(request.getToolsJson());
        profile.setToolsOther(request.getToolsOther());
        profile.setTopicsJson(request.getTopicsJson());
        profile.setTopicsOther(request.getTopicsOther());
        profile.setExperienceJson(request.getExperienceJson());
        profile.setUpdatedAt(now);

        // 职称单独同步回 user_accounts
        if (request.getTitle() != null) {
            user.setTitle(request.getTitle());
            userAccountRepository.save(user);
        }

        ReviewerProfile saved = reviewerProfileRepository.save(profile);
        return toDto(user, saved);
    }

    @Transactional
    public ReviewerProfileDto uploadIdCard(Long reviewerId, String side, MultipartFile file) {
        UserAccount user = get(reviewerId);
        LocalDateTime now = LocalDateTime.now();
        ReviewerProfile profile = reviewerProfileRepository.findById(reviewerId)
                .orElse(ReviewerProfile.builder()
                        .userId(reviewerId)
                        .createdAt(now)
                        .build());

        String newObjectName = fileStorageService.store("reviewer-id-cards/" + reviewerId, file);

        if ("FRONT".equalsIgnoreCase(side)) {
            if (profile.getIdCardFrontUrl() != null) {
                fileStorageService.delete(profile.getIdCardFrontUrl());
            }
            profile.setIdCardFrontUrl(newObjectName);
        } else if ("BACK".equalsIgnoreCase(side)) {
            if (profile.getIdCardBackUrl() != null) {
                fileStorageService.delete(profile.getIdCardBackUrl());
            }
            profile.setIdCardBackUrl(newObjectName);
        } else {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "side 参数必须为 FRONT 或 BACK");
        }
        profile.setUpdatedAt(now);
        return toDto(user, reviewerProfileRepository.save(profile));
    }

    @Transactional(readOnly = true)
    public InputStream getIdCardStream(Long reviewerId, String side) {
        ReviewerProfile profile = reviewerProfileRepository.findById(reviewerId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "档案不存在"));
        String objectName = "FRONT".equalsIgnoreCase(side)
                ? profile.getIdCardFrontUrl()
                : profile.getIdCardBackUrl();
        if (objectName == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "图片未上传");
        }
        return fileStorageService.getInputStream(objectName,
                minioProperties.getBucket().getRegistrationFiles());
    }

    @Transactional
    public void changeInstitution(Long reviewerId, ChangeInstitutionRequest req, Long operatorId, String operatorName) {
        UserAccount reviewer = get(reviewerId);
        Institution newInst = institutionRepository.findById(req.getNewInstitutionId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "机构不存在"));

        Institution oldInst = reviewer.getInstitution();
        if (oldInst != null && oldInst.getId().equals(newInst.getId())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "新机构与当前机构相同，无需变更");
        }

        ReviewerInstitutionChange change = ReviewerInstitutionChange.builder()
                .reviewerId(reviewerId)
                .oldInstitutionId(oldInst == null ? null : oldInst.getId())
                .oldInstitutionName(oldInst == null ? null : oldInst.getName())
                .newInstitutionId(newInst.getId())
                .newInstitutionName(newInst.getName())
                .reason(req.getReason())
                .changedById(operatorId)
                .changedByName(operatorName)
                .changedAt(LocalDateTime.now())
                .build();
        reviewerInstitutionChangeRepository.save(change);

        reviewer.setInstitution(newInst);
        userAccountRepository.save(reviewer);
    }

    @Transactional(readOnly = true)
    public List<ReviewerInstitutionChange> getInstitutionHistory(Long reviewerId) {
        get(reviewerId); // 校验评委存在
        return reviewerInstitutionChangeRepository.findByReviewerIdOrderByChangedAtDesc(reviewerId);
    }

    private ReviewerProfileDto toDto(UserAccount u, ReviewerProfile p) {
        return ReviewerProfileDto.builder()
                .userId(p.getUserId())
                .name(u.getName())
                .phone(u.getPhone())
                .title(u.getTitle())
                .institutionName(u.getInstitution() == null ? null : u.getInstitution().getName())
                .gender(p.getGender())
                .position(p.getPosition())
                .department(p.getDepartment())
                .idNumber(p.getIdNumber())
                .idNumberMasked(p.getIdNumberMasked())
                .idCardFrontUrl(p.getIdCardFrontUrl())
                .idCardBackUrl(p.getIdCardBackUrl())
                .bankName(p.getBankName())
                .bankCardNo(p.getBankCardNo())
                .bankCardNoMasked(p.getBankCardNoMasked())
                .backgroundsJson(p.getBackgroundsJson())
                .backgroundsOther(p.getBackgroundsOther())
                .toolsJson(p.getToolsJson())
                .toolsOther(p.getToolsOther())
                .topicsJson(p.getTopicsJson())
                .topicsOther(p.getTopicsOther())
                .experienceJson(p.getExperienceJson())
                .build();
    }
}
