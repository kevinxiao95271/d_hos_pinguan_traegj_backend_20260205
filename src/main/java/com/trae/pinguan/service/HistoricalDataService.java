package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.HistoricalData;
import com.trae.pinguan.repository.HistoricalDataRepository;
import com.trae.pinguan.web.dto.HistoricalDataQueryRequest;
import com.trae.pinguan.web.dto.HistoricalDataResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.persistence.criteria.Predicate;
import java.util.ArrayList;
import java.util.List;

/**
 * 历史数据服务
 */
@Service
@RequiredArgsConstructor
public class HistoricalDataService {
    
    private final HistoricalDataRepository historicalDataRepository;
    
    /**
     * 查询历史数据（分页+筛选）
     */
    @Transactional(readOnly = true)
    public Page<HistoricalDataResponse> queryHistoricalData(HistoricalDataQueryRequest request) {
        // 构建查询条件
        Specification<HistoricalData> spec = (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            
            // 地区筛选（从机构地址中模糊匹配）
            if (request.getRegion() != null && !request.getRegion().trim().isEmpty()) {
                predicates.add(cb.like(root.get("institutionAddress"), "%" + request.getRegion() + "%"));
            }
            
            // 组别筛选
            if (request.getCompetitionGroup() != null && !request.getCompetitionGroup().trim().isEmpty()) {
                predicates.add(cb.equal(root.get("competitionGroup"), request.getCompetitionGroup()));
            }
            
            // 品管工具/圈名筛选
            if (request.getCircleName() != null && !request.getCircleName().trim().isEmpty()) {
                predicates.add(cb.like(root.get("circleName"), "%" + request.getCircleName() + "%"));
            }
            
            // 入围状态筛选
            if (request.getDataStatus() != null && !request.getDataStatus().trim().isEmpty()) {
                predicates.add(cb.equal(root.get("dataStatus"), request.getDataStatus()));
            }
            
            // 医院名称筛选
            if (request.getInstitutionName() != null && !request.getInstitutionName().trim().isEmpty()) {
                predicates.add(cb.like(root.get("institutionName"), "%" + request.getInstitutionName() + "%"));
            }
            
            // 项目名称筛选
            if (request.getProjectName() != null && !request.getProjectName().trim().isEmpty()) {
                predicates.add(cb.like(root.get("projectName"), "%" + request.getProjectName() + "%"));
            }
            
            // 年份筛选
            if (request.getYear() != null && !request.getYear().trim().isEmpty()) {
                predicates.add(cb.equal(root.get("year"), request.getYear()));
            }
            
            return cb.and(predicates.toArray(new Predicate[0]));
        };
        
        // 构建分页和排序
        Sort sort = Sort.by(
            "DESC".equalsIgnoreCase(request.getSortDirection()) 
                ? Sort.Direction.DESC 
                : Sort.Direction.ASC,
            request.getSortBy()
        );
        
        Pageable pageable = PageRequest.of(
            request.getPage() != null ? request.getPage() : 0,
            request.getSize() != null ? request.getSize() : 20,
            sort
        );
        
        // 执行查询
        Page<HistoricalData> page = historicalDataRepository.findAll(spec, pageable);
        
        // 转换为响应对象
        return page.map(this::toResponse);
    }
    
    /**
     * 实体转响应对象
     */
    private HistoricalDataResponse toResponse(HistoricalData entity) {
        HistoricalDataResponse response = new HistoricalDataResponse();
        response.setId(entity.getId());
        response.setDataStatus(entity.getDataStatus());
        response.setInputPerson(entity.getInputPerson());
        response.setInputDate(entity.getInputDate());
        response.setYear(entity.getYear());
        response.setGroupName(entity.getGroupName());
        response.setProjectCode(entity.getProjectCode());
        response.setCompetitionGroup(entity.getCompetitionGroup());
        response.setProjectName(entity.getProjectName());
        response.setInstitutionName(entity.getInstitutionName());
        response.setInstitutionLevel(entity.getInstitutionLevel());
        response.setInstitutionAddress(entity.getInstitutionAddress());
        response.setTotalBeds(entity.getTotalBeds());
        response.setHospitalContactName(entity.getHospitalContactName());
        response.setHospitalContactTitle(entity.getHospitalContactTitle());
        response.setHospitalContactPhone(entity.getHospitalContactPhone());
        response.setHospitalContactEmail(entity.getHospitalContactEmail());
        response.setProjectLeaderName(entity.getProjectLeaderName());
        response.setProjectLeaderTitle(entity.getProjectLeaderTitle());
        response.setProjectLeaderPhone(entity.getProjectLeaderPhone());
        response.setProjectLeaderEmail(entity.getProjectLeaderEmail());
        response.setCircleName(entity.getCircleName());
        return response;
    }
}
