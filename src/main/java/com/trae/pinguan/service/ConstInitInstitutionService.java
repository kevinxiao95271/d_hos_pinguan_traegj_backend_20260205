package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.ConstInitInstitution;
import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.repository.ConstInitInstitutionRepository;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.util.RegionUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
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
 * 常量机构库Service（用于注册搜索）
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ConstInitInstitutionService {
    
    private final ConstInitInstitutionRepository constInitInstitutionRepository;
    private final InstitutionRepository institutionRepository;
    
    /**
     * 高性能搜索（注册时使用）- 支持智能地区扩展
     */
    public Page<ConstInitInstitution> search(String keyword, String region, String level, 
                                              int page, int size, String sortBy, String sortDirection) {
        Sort.Direction direction = "DESC".equalsIgnoreCase(sortDirection) 
            ? Sort.Direction.DESC 
            : Sort.Direction.ASC;
        
        Pageable pageable = PageRequest.of(page, size, Sort.by(direction, sortBy));
        
        // 智能地区扩展（市 -> 区县）
        if (region != null && !region.trim().isEmpty()) {
            List<String> expandedRegions = RegionUtils.expandRegionQuery(region);
            
            if (expandedRegions.size() > 1) {
                return searchWithExpandedRegions(keyword, expandedRegions, level, pageable);
            } else if (!expandedRegions.isEmpty()) {
                region = expandedRegions.get(0);
            }
        }
        
        return constInitInstitutionRepository.searchInstitutions(keyword, region, level, pageable);
    }
    
    /**
     * 使用扩展后的地区列表查询
     */
    private Page<ConstInitInstitution> searchWithExpandedRegions(String keyword, List<String> regions, 
                                                                   String level, Pageable pageable) {
        Specification<ConstInitInstitution> spec = (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            
            if (keyword != null && !keyword.trim().isEmpty()) {
                Predicate nameLike = cb.like(root.get("name"), "%" + keyword + "%");
                Predicate regionLike = cb.like(root.get("region"), "%" + keyword + "%");
                predicates.add(cb.or(nameLike, regionLike));
            }
            
            if (!regions.isEmpty()) {
                predicates.add(root.get("region").in(regions));
            }
            
            if (level != null && !level.trim().isEmpty()) {
                predicates.add(cb.equal(root.get("level"), level));
            }
            
            return cb.and(predicates.toArray(new Predicate[0]));
        };
        
        return constInitInstitutionRepository.findAll(spec, pageable);
    }
    
    /**
     * 自动完成
     */
    public Page<ConstInitInstitution> autocomplete(String prefix, int limit) {
        Pageable pageable = PageRequest.of(0, limit);
        return constInitInstitutionRepository.findByNameStartsWith(prefix, pageable);
    }
    
    /**
     * 获取所有地区
     */
    public List<String> getAllRegions() {
        return constInitInstitutionRepository.findAllRegions();
    }
    
    /**
     * 获取所有等级
     */
    public List<String> getAllLevels() {
        return constInitInstitutionRepository.findAllLevels();
    }
    
    /**
     * 获取热门地区
     */
    public List<Object[]> getHotRegions(int limit) {
        Pageable pageable = PageRequest.of(0, limit);
        return constInitInstitutionRepository.getHotRegions(pageable);
    }
    
    /**
     * 根据USCC查询
     */
    public ConstInitInstitution findByUscc(String uscc) {
        return constInitInstitutionRepository.findByUscc(uscc).orElse(null);
    }
    
    /**
     * 根据ID查询
     */
    public ConstInitInstitution findById(Long id) {
        return constInitInstitutionRepository.findById(id).orElse(null);
    }
    
    /**
     * 激活机构：从 const_init_institutions 同步到 institutions
     * 用于用户注册时选择机构
     * 
     * @param constInstitutionId const_init_institutions 表的ID
     * @return 同步后的 Institution ID
     */
    @Transactional
    public Long activateInstitution(Long constInstitutionId) {
        ConstInitInstitution constInst = constInitInstitutionRepository.findById(constInstitutionId)
                .orElseThrow(() -> new IllegalArgumentException("机构不存在: " + constInstitutionId));
        
        // 检查是否已经激活（在 institutions 表中存在）
        Institution existing = institutionRepository.findByUscc(constInst.getUscc()).orElse(null);
        
        if (existing != null) {
            log.info("机构已激活: {} (ID: {})", constInst.getName(), existing.getId());
            return existing.getId();
        }
        
        // 同步到 institutions 表
        Institution newInst = constInst.toInstitution();
        newInst = institutionRepository.save(newInst);
        
        log.info("激活新机构: {} (ID: {}) <- const_id: {}", 
                 newInst.getName(), newInst.getId(), constInstitutionId);
        
        return newInst.getId();
    }
}
