package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.util.RegionUtils;
import com.trae.pinguan.web.dto.InstitutionCreateRequest;
import com.trae.pinguan.web.dto.InstitutionImportRequest;
import com.trae.pinguan.web.dto.InstitutionUpdateRequest;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;
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

@Service
@RequiredArgsConstructor
public class InstitutionService {
    private final InstitutionRepository institutionRepository;

    public List<Institution> listAll() {
        return institutionRepository.findAll();
    }
    
    /**
     * 高性能搜索接口 - 支持智能地区扩展
     * 搜索"杭州市"时自动匹配所有杭州区县
     * 排序规则：等级优先（三级>二级>一级>其他），然后按名称
     */
    public Page<Institution> search(String keyword, String region, String level, int page, int size, String sortBy, String sortDirection) {
        // 使用固定的等级优先排序（不使用传入的sortBy和sortDirection）
        Pageable pageable = PageRequest.of(page, size);
        
        // 如果指定了region，智能扩展（市 -> 区县）
        if (region != null && !region.trim().isEmpty()) {
            List<String> expandedRegions = RegionUtils.expandRegionQuery(region);
            
            // 如果扩展后有多个区县，使用Specification动态查询
            if (expandedRegions.size() > 1) {
                return searchWithExpandedRegions(keyword, expandedRegions, level, pageable);
            } else if (!expandedRegions.isEmpty()) {
                // 单个地区，使用原有查询
                region = expandedRegions.get(0);
            }
        }
        
        return institutionRepository.searchInstitutions(keyword, region, level, pageable);
    }
    
    /**
     * 使用扩展后的地区列表进行查询（如杭州市的所有区县）
     * 排序规则：等级优先（三级>二级>一级>其他），然后按名称
     */
    private Page<Institution> searchWithExpandedRegions(String keyword, List<String> regions, String level, Pageable pageable) {
        Specification<Institution> spec = (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            
            // 关键词条件
            if (keyword != null && !keyword.trim().isEmpty()) {
                Predicate nameLike = cb.like(root.get("name"), "%" + keyword + "%");
                Predicate regionLike = cb.like(root.get("region"), "%" + keyword + "%");
                predicates.add(cb.or(nameLike, regionLike));
            }
            
            // 地区条件：匹配region在区县列表中，或city为对应的市
            if (!regions.isEmpty()) {
                String cityName = RegionUtils.getCityFromRegion(regions.get(0));
                
                if (cityName != null) {
                    Predicate regionIn = root.get("region").in(regions);
                    Predicate cityEqual = cb.equal(root.get("city"), cityName);
                    predicates.add(cb.or(regionIn, cityEqual));
                } else {
                    predicates.add(root.get("region").in(regions));
                }
            }
            
            // 等级条件
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
            
            return cb.and(predicates.toArray(new Predicate[0]));
        };
        
        return institutionRepository.findAll(spec, pageable);
    }
    
    /**
     * 简单搜索（保留向后兼容）
     * 注意：已强制使用等级优先排序
     */
    public Page<Institution> search(String keyword, int page, int size) {
        return search(keyword, null, null, page, size, null, null);
    }
    
    /**
     * 自动完成：按名称前缀查找
     */
    public Page<Institution> autocomplete(String prefix, int limit) {
        Pageable pageable = PageRequest.of(0, limit);
        return institutionRepository.findByNameStartsWith(prefix, pageable);
    }
    
    public Institution findByUscc(String uscc) {
        return institutionRepository.findByUscc(uscc).orElse(null);
    }
    
    public List<Institution> findByRegion(String region) {
        return institutionRepository.findByRegion(region);
    }
    
    public List<String> getAllRegions() {
        return institutionRepository.findAllRegions();
    }
    
    public List<String> getAllLevels() {
        return institutionRepository.findAllLevels();
    }
    
    /**
     * 获取热门地区（带机构数量）
     */
    public List<Object[]> getHotRegions(int limit) {
        Pageable pageable = PageRequest.of(0, limit);
        return institutionRepository.getHotRegions(pageable);
    }
    
    /**
     * 统计各地区机构数量
     */
    public List<Object[]> getRegionStats() {
        return institutionRepository.countByRegion();
    }

    public Institution get(Long id) {
        return institutionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("机构不存在"));
    }

    @Transactional
    public Institution create(InstitutionCreateRequest request) {
        institutionRepository.findByUscc(request.getUscc()).ifPresent(item -> {
            throw new IllegalArgumentException("统一社会信用代码已存在");
        });
        Institution institution = Institution.builder()
                .name(request.getName())
                .code(request.getCode())
                .uscc(request.getUscc())
                .region(request.getRegion())
                .createdAt(LocalDateTime.now())
                .build();
        return institutionRepository.save(institution);
    }

    @Transactional
    public Institution update(Long id, InstitutionUpdateRequest request) {
        Institution institution = get(id);
        if (request.getName() != null) {
            institution.setName(request.getName());
        }
        if (request.getCode() != null) {
            institution.setCode(request.getCode());
        }
        if (request.getUscc() != null && !request.getUscc().equals(institution.getUscc())) {
            institutionRepository.findByUscc(request.getUscc()).ifPresent(item -> {
                throw new IllegalArgumentException("统一社会信用代码已存在");
            });
            institution.setUscc(request.getUscc());
        }
        if (request.getRegion() != null) {
            institution.setRegion(request.getRegion());
        }
        return institutionRepository.save(institution);
    }

    @Transactional
    public void delete(Long id) {
        if (!institutionRepository.existsById(id)) {
            throw new IllegalArgumentException("机构不存在");
        }
        institutionRepository.deleteById(id);
    }

    @Transactional
    public List<Institution> importInstitutions(InstitutionImportRequest request) {
        List<Institution> items = request.getItems().stream()
                .map(item -> Institution.builder()
                        .name(item.getName())
                        .code(item.getCode())
                        .uscc(item.getUscc())
                        .region(item.getRegion())
                        .createdAt(LocalDateTime.now())
                        .build())
                .collect(Collectors.toList());
        return institutionRepository.saveAll(items);
    }
}
