package com.trae.pinguan.domain.entity;

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
@Table(name = "institutions")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class Institution {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(nullable = false, length = 64, unique = true)
    private String code;

    @Column(nullable = false, length = 32, unique = true)
    private String uscc;

    @Column(length = 64)
    private String region;
    
    @Column(length = 32)
    private String level;

    @Column(nullable = false)
    private LocalDateTime createdAt;
}
