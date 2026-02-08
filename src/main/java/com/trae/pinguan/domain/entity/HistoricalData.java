package com.trae.pinguan.domain.entity;

import lombok.Data;

import javax.persistence.*;

/**
 * 历史数据实体
 * 独立表，不与其他业务表关联
 */
@Data
@Entity
@Table(name = "pinguan_his_data")
public class HistoricalData {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    
    @Column(name = "data_status", columnDefinition = "TEXT")
    private String dataStatus;
    
    @Column(name = "input_person", columnDefinition = "TEXT")
    private String inputPerson;
    
    @Column(name = "input_date", columnDefinition = "TEXT")
    private String inputDate;
    
    @Column(name = "year", columnDefinition = "TEXT")
    private String year;
    
    @Column(name = "group_name", columnDefinition = "TEXT")
    private String groupName;
    
    @Column(name = "project_code", columnDefinition = "TEXT")
    private String projectCode;
    
    @Column(name = "competition_group", columnDefinition = "TEXT")
    private String competitionGroup;
    
    @Column(name = "project_name", columnDefinition = "TEXT")
    private String projectName;
    
    @Column(name = "institution_name", columnDefinition = "TEXT")
    private String institutionName;
    
    @Column(name = "institution_level", columnDefinition = "TEXT")
    private String institutionLevel;
    
    @Column(name = "institution_address", columnDefinition = "TEXT")
    private String institutionAddress;
    
    @Column(name = "total_beds", columnDefinition = "TEXT")
    private String totalBeds;
    
    @Column(name = "hospital_contact_name", columnDefinition = "TEXT")
    private String hospitalContactName;
    
    @Column(name = "hospital_contact_title", columnDefinition = "TEXT")
    private String hospitalContactTitle;
    
    @Column(name = "hospital_contact_phone", columnDefinition = "TEXT")
    private String hospitalContactPhone;
    
    @Column(name = "hospital_contact_email", columnDefinition = "TEXT")
    private String hospitalContactEmail;
    
    @Column(name = "project_leader_name", columnDefinition = "TEXT")
    private String projectLeaderName;
    
    @Column(name = "project_leader_title", columnDefinition = "TEXT")
    private String projectLeaderTitle;
    
    @Column(name = "project_leader_phone", columnDefinition = "TEXT")
    private String projectLeaderPhone;
    
    @Column(name = "project_leader_email", columnDefinition = "TEXT")
    private String projectLeaderEmail;
    
    @Column(name = "circle_name", columnDefinition = "TEXT")
    private String circleName;
}
