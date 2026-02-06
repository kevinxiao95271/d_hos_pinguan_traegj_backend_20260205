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
@Table(name = "competition_templates")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class CompetitionTemplate {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "competition_id")
    @JsonIgnore
    private Competition competition;

    @Column(nullable = false, length = 64)
    private String type;

    @Column(nullable = false, length = 200)
    private String fileName;

    @Column(nullable = false, length = 300)
    private String fileUrl;

    @Column(nullable = false)
    private LocalDateTime uploadedAt;
}
