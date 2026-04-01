package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.time.LocalDateTime;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Lob;
import javax.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "reviewer_profiles")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ReviewerProfile {
    @Id
    @Column(name = "user_id")
    private Long userId;

    @Column(length = 8)
    private String gender;

    @Column(name = "job_position", length = 64)
    private String position;

    @Column(name = "id_number", length = 64)
    private String idNumber;

    @Column(name = "id_number_masked", length = 32)
    private String idNumberMasked;

    @Column(name = "id_card_front_url", length = 500)
    private String idCardFrontUrl;

    @Column(name = "id_card_back_url", length = 500)
    private String idCardBackUrl;

    @Column(name = "bank_name", length = 128)
    private String bankName;

    @Column(name = "bank_card_no", length = 128)
    private String bankCardNo;

    @Column(name = "bank_card_no_masked", length = 32)
    private String bankCardNoMasked;

    @Lob
    @Column(name = "backgrounds_json")
    private String backgroundsJson;

    @Lob
    @Column(name = "tools_json")
    private String toolsJson;

    @Lob
    @Column(name = "topics_json")
    private String topicsJson;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
}
