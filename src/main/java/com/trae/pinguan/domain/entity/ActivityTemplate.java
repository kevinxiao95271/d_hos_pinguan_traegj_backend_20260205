package com.trae.pinguan.domain.entity;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.time.LocalDateTime;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
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
@Table(name = "activity_templates")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ActivityTemplate {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 64)
    private String type;

    @Column(nullable = false, length = 200)
    private String fileName;

    @Column(nullable = false, length = 300)
    private String fileUrl;

    @Column(nullable = false)
    private LocalDateTime uploadedAt;
}
