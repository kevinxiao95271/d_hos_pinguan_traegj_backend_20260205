package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.ReviewerIntegrityNotice;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReviewerIntegrityNoticeRepository extends JpaRepository<ReviewerIntegrityNotice, Long> {

    List<ReviewerIntegrityNotice> findByUserId(Long userId);

    Optional<ReviewerIntegrityNotice> findByUserIdAndNoticeKey(Long userId, String noticeKey);

    boolean existsByUserIdAndNoticeKey(Long userId, String noticeKey);
}
