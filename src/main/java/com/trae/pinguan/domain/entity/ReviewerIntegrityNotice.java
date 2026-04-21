package com.trae.pinguan.domain.entity;

import java.time.LocalDateTime;
import javax.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(
    name = "reviewer_integrity_notices",
    uniqueConstraints = @UniqueConstraint(
        name = "uk_rin_user_key",
        columnNames = {"user_id", "notice_key"}
    )
)
public class ReviewerIntegrityNotice {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 评审专家 ID，关联 user_accounts.id */
    @Column(name = "user_id", nullable = false)
    private Long userId;

    /** 须知标识，如 BOOK / INTERVIEW，与前端 integrityNotices.js 对齐 */
    @Column(name = "notice_key", nullable = false, length = 32)
    private String noticeKey;

    @Column(name = "confirmed_at", nullable = false)
    private LocalDateTime confirmedAt;
}
