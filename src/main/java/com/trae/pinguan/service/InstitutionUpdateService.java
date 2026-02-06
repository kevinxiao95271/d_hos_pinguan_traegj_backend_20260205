package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.domain.entity.InstitutionUpdateRequest;
import com.trae.pinguan.domain.entity.UserAccount;
import com.trae.pinguan.domain.enums.ApprovalStatus;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.repository.InstitutionUpdateRequestRepository;
import com.trae.pinguan.repository.UserAccountRepository;
import com.trae.pinguan.web.dto.InstitutionUpdateReviewRequest;
import com.trae.pinguan.web.dto.InstitutionUpdateSubmitRequest;
import java.time.LocalDateTime;
import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class InstitutionUpdateService {
    private final InstitutionUpdateRequestRepository updateRequestRepository;
    private final InstitutionRepository institutionRepository;
    private final UserAccountRepository userAccountRepository;

    public List<InstitutionUpdateRequest> listPending() {
        return updateRequestRepository.findByStatus(ApprovalStatus.PENDING);
    }

    @Transactional
    public InstitutionUpdateRequest submit(InstitutionUpdateSubmitRequest request) {
        Institution institution = institutionRepository.findById(request.getInstitutionId())
                .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
        UserAccount submitter = userAccountRepository.findById(request.getSubmitterId())
                .orElseThrow(() -> new IllegalArgumentException("提交人不存在"));
        InstitutionUpdateRequest updateRequest = InstitutionUpdateRequest.builder()
                .institution(institution)
                .submitter(submitter)
                .newName(request.getNewName())
                .newCode(request.getNewCode())
                .newUscc(request.getNewUscc())
                .status(ApprovalStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .build();
        return updateRequestRepository.save(updateRequest);
    }

    @Transactional
    public InstitutionUpdateRequest review(InstitutionUpdateReviewRequest request) {
        InstitutionUpdateRequest updateRequest = updateRequestRepository.findById(request.getRequestId())
                .orElseThrow(() -> new IllegalArgumentException("申请不存在"));
        updateRequest.setStatus(request.getStatus());
        updateRequest.setReviewedAt(LocalDateTime.now());
        if (request.getStatus() == ApprovalStatus.APPROVED) {
            Institution institution = updateRequest.getInstitution();
            if (updateRequest.getNewName() != null) {
                institution.setName(updateRequest.getNewName());
            }
            if (updateRequest.getNewCode() != null) {
                institution.setCode(updateRequest.getNewCode());
            }
            if (updateRequest.getNewUscc() != null) {
                institution.setUscc(updateRequest.getNewUscc());
            }
            institutionRepository.save(institution);
        }
        return updateRequestRepository.save(updateRequest);
    }
}
