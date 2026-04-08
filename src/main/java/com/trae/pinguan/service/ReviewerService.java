package com.trae.pinguan.service;

import com.trae.pinguan.config.MinioProperties;
import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.domain.entity.ReviewerProfile;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.repository.ReviewerProfileRepository;
import com.trae.pinguan.repository.UserAccountRepository;
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
        get(reviewerId); // 校验评委存在
        ReviewerProfile profile = reviewerProfileRepository.findById(reviewerId)
                .orElse(null);
        if (profile == null) {
            return ReviewerProfileDto.builder().userId(reviewerId).build();
        }
        return toDto(profile);
    }

    @Transactional
    public ReviewerProfileDto upsertProfile(Long reviewerId, ReviewerProfileUpsertRequest request) {
        get(reviewerId); // 校验评委存在
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
        profile.setBankName(request.getBankName());
        profile.setBankCardNo(request.getBankCardNo());
        profile.setBankCardNoMasked(request.getBankCardNoMasked());
        profile.setBackgroundsJson(request.getBackgroundsJson());
        profile.setToolsJson(request.getToolsJson());
        profile.setTopicsJson(request.getTopicsJson());
        profile.setUpdatedAt(now);

        ReviewerProfile saved = reviewerProfileRepository.save(profile);
        return toDto(saved);
    }

    @Transactional
    public ReviewerProfileDto uploadIdCard(Long reviewerId, String side, MultipartFile file) {
        get(reviewerId);
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
        return toDto(reviewerProfileRepository.save(profile));
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

    private ReviewerProfileDto toDto(ReviewerProfile p) {
        return ReviewerProfileDto.builder()
                .userId(p.getUserId())
                .gender(p.getGender())
                .position(p.getPosition())
                .idNumber(p.getIdNumber())
                .idNumberMasked(p.getIdNumberMasked())
                .idCardFrontUrl(p.getIdCardFrontUrl())
                .idCardBackUrl(p.getIdCardBackUrl())
                .bankName(p.getBankName())
                .bankCardNo(p.getBankCardNo())
                .bankCardNoMasked(p.getBankCardNoMasked())
                .backgroundsJson(p.getBackgroundsJson())
                .toolsJson(p.getToolsJson())
                .topicsJson(p.getTopicsJson())
                .build();
    }
}
