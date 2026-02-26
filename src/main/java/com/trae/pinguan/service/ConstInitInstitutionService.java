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
     * 排序规则：等级优先（三级>二级>一级>其他），然后按名称
     */
    public Page<ConstInitInstitution> search(String keyword, String region, String level, 
                                              int page, int size, String sortBy, String sortDirection) {
        // 使用自定义排序：等级优先（降序），然后按名称（升序）
        Pageable pageable = PageRequest.of(page, size);
        
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
     * 排序规则：等级优先（三级>二级>一级>其他），然后按名称
     */
    private Page<ConstInitInstitution> searchWithExpandedRegions(String keyword, List<String> regions, 
                                                                   String level, Pageable pageable) {
        Specification<ConstInitInstitution> spec = (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            
            // 关键词搜索（空字符串视为无条件）
            if (keyword != null && !keyword.trim().isEmpty()) {
                Predicate nameLike = cb.like(root.get("name"), "%" + keyword + "%");
                Predicate regionLike = cb.like(root.get("region"), "%" + keyword + "%");
                predicates.add(cb.or(nameLike, regionLike));
            }
            
            // 地区筛选：匹配region在区县列表中，或city为对应的市
            if (!regions.isEmpty()) {
                // 推断城市名（从第一个region推断）
                String cityName = RegionUtils.getCityFromRegion(regions.get(0));
                
                if (cityName != null) {
                    // region在区县列表中 OR city等于该市
                    Predicate regionIn = root.get("region").in(regions);
                    Predicate cityEqual = cb.equal(root.get("city"), cityName);
                    predicates.add(cb.or(regionIn, cityEqual));
                } else {
                    // 无法推断城市，只用region匹配
                    predicates.add(root.get("region").in(regions));
                }
            }
            
            // 等级筛选（空字符串视为无条件）
            if (level != null && !level.trim().isEmpty()) {
                predicates.add(cb.equal(root.get("level"), level));
            }
            
            // 自定义排序：等级优先（三级>二级>一级>其他），然后按名称
            if (query != null) {
                query.orderBy(
                    cb.asc(
                        cb.selectCase()
                            .when(cb.equal(root.get("level"), "三级"), 1)
                            .when(cb.equal(root.get("level"), "二级"), 2)
                            .when(cb.equal(root.get("level"), "一级"), 3)
                            .otherwise(4)
                    ),
                    cb.asc(root.get("name"))
                );
            }
            
            // 如果没有任何条件，返回所有结果
            if (predicates.isEmpty()) {
                return cb.conjunction();
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
