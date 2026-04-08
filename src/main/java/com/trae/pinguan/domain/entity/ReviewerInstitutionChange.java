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
@Table(name = "reviewer_institution_changes")
public class ReviewerInstitutionChange {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "reviewer_id", nullable = false)
    private Long reviewerId;

    @Column(name = "old_institution_id")
    private Long oldInstitutionId;

    @Column(name = "old_institution_name", length = 256)
    private String oldInstitutionName;

    @Column(name = "new_institution_id")
    private Long newInstitutionId;

    @Column(name = "new_institution_name", length = 256)
    private String newInstitutionName;

    /** 申请原因/备注 */
    @Column(length = 500)
    private String reason;

    /** 操作人ID（可以是本人也可以是管理员） */
    @Column(name = "changed_by_id")
    private Long changedById;

    @Column(name = "changed_by_name", length = 64)
    private String changedByName;

    @Column(name = "changed_at", nullable = false)
    private LocalDateTime changedAt;
}
