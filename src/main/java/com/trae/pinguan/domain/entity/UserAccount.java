package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.trae.pinguan.domain.enums.RoleType;
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
@Table(name = "user_accounts")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class UserAccount {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 32, unique = true)
    private String phone;

    @Column(nullable = false, length = 64)
    private String name;

    @Column(length = 64)
    private String title;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private RoleType role;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "institution_id")
    @JsonIgnore
    private Institution institution;

    @Column(length = 32)
    private String reviewerGroupCode;

    @Column(length = 32)
    private String interviewGroupCode;

    @Column(length = 32)
    private String expertBackground;

    @Column(nullable = false)
    private LocalDateTime createdAt;
}
