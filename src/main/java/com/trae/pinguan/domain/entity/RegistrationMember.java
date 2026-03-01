package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.trae.pinguan.domain.enums.MemberRole;
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
@Table(name = "registration_members")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class RegistrationMember {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "registration_id")
    @JsonIgnore
    private Registration registration;

    @Column(name = "registration_id", insertable = false, updatable = false)
    private Long registrationId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private MemberRole role;

    @Column(nullable = false, length = 64)
    private String name;

    @Column(nullable = false, length = 64)
    private String title;

    @Column(length = 64)
    private String department;
}
