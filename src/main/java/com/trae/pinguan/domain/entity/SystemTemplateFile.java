package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
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
@Table(name = "system_template_files")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class SystemTemplateFile {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 64)
    private String templateType;
    
    @Column(nullable = false, length = 200)
    private String fileName;
    
    @Column(nullable = false, length = 300)
    private String minioObjectName;
    
    @Column(nullable = false)
    private Long fileSize;
    
    @Column(nullable = false)
    private Integer version;
    
    @Column(nullable = false)
    private Boolean isActive;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "uploaded_by")
    @JsonIgnore
    private UserAccount uploadedBy;
    
    @Column(nullable = false)
    private LocalDateTime uploadedAt;
    
    @Column(length = 500)
    private String description;
}
