package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.StaffSessionAssignment;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StaffSessionAssignmentRepository extends JpaRepository<StaffSessionAssignment, Long> {
    List<StaffSessionAssignment> findByStaffId(Long staffId);
    boolean existsByStaffIdAndSessionCode(Long staffId, String sessionCode);
}
