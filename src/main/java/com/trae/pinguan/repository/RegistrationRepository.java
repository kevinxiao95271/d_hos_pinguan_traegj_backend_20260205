package com.trae.pinguan.repository;

import com.trae.pinguan.domain.entity.Registration;
import com.trae.pinguan.domain.enums.GroupType;
import com.trae.pinguan.domain.enums.RegistrationStatus;
import com.trae.pinguan.web.dto.RegistrationFilterItem;
import java.util.List;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.query.Param;

public interface RegistrationRepository extends JpaRepository<Registration, Long> {
    List<Registration> findByCompetitionId(Long competitionId);
    long countByCompetitionId(Long competitionId);

    /** 判断该赛事下是否已有任何已分组记录（group_code 非空） */
    @Query("SELECT COUNT(r) > 0 FROM Registration r WHERE r.competition.id = :competitionId AND r.groupCode IS NOT NULL AND r.groupCode <> ''")
    boolean existsGroupedByCompetitionId(@Param("competitionId") Long competitionId);
    List<Registration> findByCompetitionIdAndStatus(Long competitionId, RegistrationStatus status);
    List<Registration> findByApplicantId(Long applicantId);
    List<Registration> findByInstitutionId(Long institutionId);

    @Query("select r from Registration r join fetch r.institution where r.competition.id = :competitionId")
    List<Registration> findByCompetitionIdWithInstitution(@Param("competitionId") Long competitionId);

    @Query("select r from Registration r left join fetch r.institution where r.id in :ids")
    List<Registration> findByIdInWithInstitution(@Param("ids") java.util.Collection<Long> ids);

    @Query("select count(r) from Registration r where r.competition.id = :competitionId " +
            "and r.institution.id = :institutionId " +
            "and r.status in (com.trae.pinguan.domain.enums.RegistrationStatus.SUBMITTED, " +
            "com.trae.pinguan.domain.enums.RegistrationStatus.APPROVED)")
    long countActiveByCompetitionAndInstitution(@Param("competitionId") Long competitionId,
                                                @Param("institutionId") Long institutionId);

    // ── 现场竞赛 ──────────────────────────────────────────────────────────────

    @Query("select distinct r.finalSessionDate, r.finalSessionCode from Registration r " +
           "where r.competition.id = :competitionId and r.finalSessionCode is not null " +
           "order by r.finalSessionDate asc, r.finalSessionCode asc")
    List<Object[]> findDistinctFinalSessionsByCompetitionId(@Param("competitionId") Long competitionId);

    @Query("select distinct r.finalSessionCode from Registration r " +
           "where r.competition.id = :competitionId and r.finalSessionCode is not null " +
           "order by r.finalSessionCode")
    List<String> findDistinctFinalSessionCodesByCompetitionId(@Param("competitionId") Long competitionId);

    @Query("select r from Registration r join fetch r.institution " +
           "where r.competition.id = :competitionId and r.finalSessionCode = :sessionCode " +
           "order by r.finalSessionOrder asc nulls last")
    List<Registration> findByCompetitionIdAndFinalSessionCode(
            @Param("competitionId") Long competitionId,
            @Param("sessionCode") String sessionCode);

    @Query("select r from Registration r where r.competition.id = :competitionId " +
           "and r.finalSessionCode is not null")
    List<Registration> findAllWithFinalSessionByCompetitionId(@Param("competitionId") Long competitionId);

    @Query(value = "select new com.trae.pinguan.web.dto.RegistrationFilterItem(" +
            "r.id, r.projectName, i.name, i.level, r.groupType, r.groupCode, r.status, r.submittedAt, " +
            "a.subjectTypeCode, a.methodCode, '', '', r.applicant.name) " +
            "from Registration r " +
            "join r.institution i " +
            "left join ActivityInfo a on a.registration = r " +
            "where r.competition.id = :competitionId " +
            "and r.status <> com.trae.pinguan.domain.enums.RegistrationStatus.DRAFT " +
            "and (:status is null or r.status = :status) " +
            "and (:groupType is null or r.groupType = :groupType) " +
            "and (:groupCode is null or r.groupCode = :groupCode) " +
            "and (:registrationCode is null or r.registrationCode = :registrationCode) " +
            "and (:projectName is null or r.projectName like concat('%', :projectName, '%')) " +
            "and (:institutionName is null or i.name like concat('%', :institutionName, '%')) " +
            "and (:methodCode is null or a.methodCode = :methodCode) " +
            "and (:subjectTypeCode is null or a.subjectTypeCode = :subjectTypeCode) " +
            "and (:hasPaymentProof is null or " +
            "(:hasPaymentProof = true and exists (select 1 from MaterialFile m where m.registration = r and m.type = 'payment_proof')) or " +
            "(:hasPaymentProof = false and not exists (select 1 from MaterialFile m where m.registration = r and m.type = 'payment_proof')))",
            countQuery = "select count(r) " +
            "from Registration r " +
            "join r.institution i " +
            "left join ActivityInfo a on a.registration = r " +
            "where r.competition.id = :competitionId " +
            "and r.status <> com.trae.pinguan.domain.enums.RegistrationStatus.DRAFT " +
            "and (:status is null or r.status = :status) " +
            "and (:groupType is null or r.groupType = :groupType) " +
            "and (:groupCode is null or r.groupCode = :groupCode) " +
            "and (:registrationCode is null or r.registrationCode = :registrationCode) " +
            "and (:projectName is null or r.projectName like concat('%', :projectName, '%')) " +
            "and (:institutionName is null or i.name like concat('%', :institutionName, '%')) " +
            "and (:methodCode is null or a.methodCode = :methodCode) " +
            "and (:subjectTypeCode is null or a.subjectTypeCode = :subjectTypeCode) " +
            "and (:hasPaymentProof is null or " +
            "(:hasPaymentProof = true and exists (select 1 from MaterialFile m where m.registration = r and m.type = 'payment_proof')) or " +
            "(:hasPaymentProof = false and not exists (select 1 from MaterialFile m where m.registration = r and m.type = 'payment_proof')))")
    Page<RegistrationFilterItem> filterRegistrations(@Param("competitionId") Long competitionId,
                                                     @Param("status") RegistrationStatus status,
                                                     @Param("groupType") GroupType groupType,
                                                     @Param("groupCode") String groupCode,
                                                     @Param("registrationCode") Integer registrationCode,
                                                     @Param("projectName") String projectName,
                                                     @Param("institutionName") String institutionName,
                                                     @Param("methodCode") String methodCode,
                                                     @Param("subjectTypeCode") String subjectTypeCode,
                                                     @Param("hasPaymentProof") Boolean hasPaymentProof,
                                                     Pageable pageable);

    /** 按赛事获取当前最大 registrationCode（用于生成下一个编号），无已提交记录时返回 empty */
    @Query("select max(r.registrationCode) from Registration r where r.competition.id = :competitionId")
    Optional<Integer> findMaxRegistrationCodeByCompetitionId(@Param("competitionId") Long competitionId);
}
