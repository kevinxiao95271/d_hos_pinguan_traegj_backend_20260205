package com.trae.pinguan.domain.entity;

import javax.persistence.*;
import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "staff_session_assignments",
       uniqueConstraints = @UniqueConstraint(columnNames = {"staff_id", "session_code"}))
public class StaffSessionAssignment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "staff_id", nullable = false)
    private Long staffId;

    @Column(name = "session_code", nullable = false, length = 128)
    private String sessionCode;
}
