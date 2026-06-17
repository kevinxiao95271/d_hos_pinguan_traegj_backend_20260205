package com.trae.pinguan.service;

import com.trae.pinguan.config.MinioProperties;
import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.domain.entity.ReviewTask;
import com.trae.pinguan.domain.entity.ReviewerInstitutionChange;
import com.trae.pinguan.domain.entity.ReviewerProfile;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.ReviewStage;
import com.trae.pinguan.domain.enums.ReviewStatus;
import com.trae.pinguan.domain.enums.RoleType;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.repository.ReviewTaskRepository;
import com.trae.pinguan.repository.ReviewerInstitutionChangeRepository;
import com.trae.pinguan.repository.ReviewerProfileRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.ChangeInstitutionRequest;
import com.trae.pinguan.web.dto.ReviewerExportRow;
import com.trae.pinguan.web.dto.ReviewerListItem;
import com.trae.pinguan.web.dto.ReviewerProfileDto;
import com.trae.pinguan.web.dto.ReviewerProfileUpsertRequest;
import com.trae.pinguan.web.dto.ReviewerUpsertRequest;
import java.io.InputStream;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
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
    private final ReviewTaskRepository reviewTaskRepository;
    private final FileStorageService fileStorageService;
    private final MinioProperties minioProperties;

    @Transactional(readOnly = true)
    public List<ReviewerListItem> list(Long institutionId,
                                       String reviewerGroupCode,
                                       String interviewGroupCode,
                                       String expertBackground) {
        return list(null, institutionId, reviewerGroupCode, interviewGroupCode, expertBackground);
    }

    public List<ReviewerListItem> list(Long competitionId,
                                       Long institutionId,
                                       String reviewerGroupCode,
                                       String interviewGroupCode,
                                       String expertBackground) {
        // 预加载评委决赛任务（仅当传入 competitionId 时查询）
        Map<Long, List<String>> finalSessionsByReviewer = new HashMap<>();
        if (competitionId != null) {
            List<ReviewTask> finalTasks = reviewTaskRepository
                    .findWithDetailsByStageAndCompetitionId(ReviewStage.FINAL, competitionId);
            for (ReviewTask t : finalTasks) {
                if (t.getReviewer() == null) continue;
                String sessionCode = t.getRegistration() != null
                        ? t.getRegistration().getFinalSessionCode() : null;
                if (sessionCode == null) continue;
                finalSessionsByReviewer
                        .computeIfAbsent(t.getReviewer().getId(), k -> new ArrayList<>())
                        .add(sessionCode);
            }
            // 每个评委的 sessionCodes 去重排序
            finalSessionsByReviewer.replaceAll((k, v) ->
                    v.stream().distinct().sorted().collect(Collectors.toList()));
        }

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
                        user.getExpertBackground(),
                        finalSessionsByReviewer.getOrDefault(user.getId(), new ArrayList<>())
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
        if (request.getIdNumber() != null) {
            profile.setIdNumber(request.getIdNumber());
            profile.setIdNumberMasked(maskIdNumber(request.getIdNumber()));
        }
        profile.setIdCardFrontUrl(request.getIdCardFrontUrl());
        profile.setIdCardBackUrl(request.getIdCardBackUrl());
        profile.setDepartment(request.getDepartment());
        profile.setBankName(request.getBankName());
        if (request.getBankCardNo() != null) {
            profile.setBankCardNo(request.getBankCardNo());
            profile.setBankCardNoMasked(maskBankCardNo(request.getBankCardNo()));
        }
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

    /**
     * 返回所有已上传身份证照片的评委（含 objectName）供批量打包下载
     * 每条记录：[userId, name, institutionName, frontObjectName, backObjectName]
     * frontObjectName / backObjectName 可能为 null（未上传）
     */
    @Transactional(readOnly = true)
    public List<Object[]> listIdCardEntries() {
        List<UserAccount> reviewers = userAccountRepository.findByRoleWithInstitution(RoleType.REVIEWER);
        Map<Long, ReviewerProfile> profileMap = reviewerProfileRepository.findAll().stream()
                .collect(Collectors.toMap(ReviewerProfile::getUserId, p -> p, (a, b) -> a));
        List<Object[]> result = new ArrayList<>();
        for (UserAccount u : reviewers) {
            ReviewerProfile p = profileMap.get(u.getId());
            if (p == null) continue;
            if (p.getIdCardFrontUrl() == null && p.getIdCardBackUrl() == null) continue;
            String instName = u.getInstitution() == null ? "未知机构" : u.getInstitution().getName();
            result.add(new Object[]{
                u.getId(), u.getName(), instName,
                p.getIdCardFrontUrl(), p.getIdCardBackUrl()
            });
        }
        return result;
    }

    public InputStream getIdCardStreamByObjectName(String objectName) {
        return fileStorageService.getInputStream(objectName,
                minioProperties.getBucket().getRegistrationFiles());
    }

    /**
     * 批量导出：所有评委基本信息 + 扩展档案 + 任务统计
     */
    @Transactional(readOnly = true)
    public List<ReviewerExportRow> buildExportRows() {
        return buildExportRows(null);
    }

    public List<ReviewerExportRow> buildExportRows(Long competitionId) {
        List<UserAccount> reviewers = userAccountRepository.findByRoleWithInstitution(RoleType.REVIEWER);
        Map<Long, ReviewerProfile> profileMap = reviewerProfileRepository.findAll().stream()
                .collect(Collectors.toMap(ReviewerProfile::getUserId, p -> p, (a, b) -> a));

        // 任务状态统计：reviewer_id → (status → count)
        Map<Long, Map<ReviewStatus, Long>> statsMap = new HashMap<>();
        for (Object[] row : reviewTaskRepository.countByReviewerIdGroupByStatus()) {
            Long reviewerId = ((Number) row[0]).longValue();
            ReviewStatus status = (ReviewStatus) row[1];
            long count = ((Number) row[2]).longValue();
            statsMap.computeIfAbsent(reviewerId, k -> new HashMap<>()).put(status, count);
        }

        // 决赛分配场次统计（可选）
        Map<Long, String> finalSessionsTextByReviewer = new HashMap<>();
        if (competitionId != null) {
            List<ReviewTask> finalTasks = reviewTaskRepository
                    .findWithDetailsByStageAndCompetitionId(ReviewStage.FINAL, competitionId);
            Map<Long, List<String>> byReviewer = new HashMap<>();
            for (ReviewTask t : finalTasks) {
                if (t.getReviewer() == null) continue;
                String sc = t.getRegistration() != null ? t.getRegistration().getFinalSessionCode() : null;
                if (sc == null) continue;
                byReviewer.computeIfAbsent(t.getReviewer().getId(), k -> new ArrayList<>()).add(sc);
            }
            byReviewer.forEach((rid, list) ->
                    finalSessionsTextByReviewer.put(rid,
                            list.stream().distinct().sorted().collect(Collectors.joining(","))));
        }

        List<ReviewerExportRow> result = new ArrayList<>();
        for (UserAccount u : reviewers) {
            ReviewerProfile p = profileMap.get(u.getId());
            Map<ReviewStatus, Long> stats = statsMap.getOrDefault(u.getId(), new HashMap<>());
            result.add(ReviewerExportRow.builder()
                    .userId(u.getId())
                    .name(u.getName())
                    .phone(u.getPhone())
                    .title(u.getTitle())
                    .institutionName(u.getInstitution() == null ? null : u.getInstitution().getName())
                    .expertBackground(u.getExpertBackground())
                    .gender(p == null ? null : p.getGender())
                    .department(p == null ? null : p.getDepartment())
                    .position(p == null ? null : p.getPosition())
                    .idNumber(p == null ? null : p.getIdNumber())
                    .idCardFront(p == null ? null : (p.getIdCardFrontUrl() != null ? "已上传" : "未上传"))
                    .idCardBack(p == null ? null : (p.getIdCardBackUrl() != null ? "已上传" : "未上传"))
                    .bankName(p == null ? null : p.getBankName())
                    .bankCardNo(p == null ? null : p.getBankCardNo())
                    .backgroundsJson(p == null ? null : p.getBackgroundsJson())
                    .backgroundsOther(p == null ? null : p.getBackgroundsOther())
                    .toolsJson(p == null ? null : p.getToolsJson())
                    .toolsOther(p == null ? null : p.getToolsOther())
                    .topicsJson(p == null ? null : p.getTopicsJson())
                    .topicsOther(p == null ? null : p.getTopicsOther())
                    .experienceJson(p == null ? null : p.getExperienceJson())
                    .taskScored(stats.getOrDefault(ReviewStatus.SCORED, 0L))
                    .taskDraft(stats.getOrDefault(ReviewStatus.DRAFT, 0L))
                    .taskPending(stats.getOrDefault(ReviewStatus.PENDING, 0L))
                    .taskRecused(stats.getOrDefault(ReviewStatus.RECUSED, 0L))
                    .finalSessionCodes(finalSessionsTextByReviewer.get(u.getId()))
                    .build());
        }
        result.sort((a, b) -> {
            String ia = a.getInstitutionName() == null ? "" : a.getInstitutionName();
            String ib = b.getInstitutionName() == null ? "" : b.getInstitutionName();
            int c = ia.compareTo(ib);
            return c != 0 ? c : (a.getName() == null ? "" : a.getName())
                    .compareTo(b.getName() == null ? "" : b.getName());
        });
        return result;
    }

    /** 身份证脱敏：保留前6位和后4位，中间用 **** 替换 */
    private String maskIdNumber(String idNumber) {
        if (idNumber == null || idNumber.length() < 10) return idNumber;
        return idNumber.substring(0, 6) + "********" + idNumber.substring(idNumber.length() - 4);
    }

    /** 银行卡脱敏：保留前4位和后4位，中间用 **** 替换 */
    private String maskBankCardNo(String cardNo) {
        if (cardNo == null || cardNo.length() < 8) return cardNo;
        return cardNo.substring(0, 4) + " **** **** " + cardNo.substring(cardNo.length() - 4);
    }
}
