package com.trae.pinguan.domain.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.LocalDateTime;

/**
 * 常量初始化机构表（36K+，仅用于注册时搜索）
 * 不参与业务流程，用户选择后自动同步到 Institution 表
 */
@Entity
@Table(name = "const_init_institutions")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConstInitInstitution {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true, length = 64)
    private String code;
    
    @Column(nullable = false, unique = true, length = 32)
    private String uscc;
    
    @Column(nullable = false, length = 200)
    private String name;
    
    @Column(length = 64)
    private String region;
    
    @Column(length = 50)
    private String city;
    
    @Column(length = 32)
    private String level;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }
    
    /**
     * 转换为 Institution 实体（用于同步）
     */
    public Institution toInstitution() {
        return Institution.builder()
                .code(this.code)
                .uscc(this.uscc)
                .name(this.name)
                .region(this.region)
                .city(this.city)
                .level(this.level)
                .createdAt(java.time.LocalDateTime.now())
                .build();
    }
}
