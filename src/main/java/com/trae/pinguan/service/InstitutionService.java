package com.trae.pinguan.service;

import com.trae.pinguan.domain.entity.Institution;
import com.trae.pinguan.repository.InstitutionRepository;
import com.trae.pinguan.web.dto.InstitutionCreateRequest;
import com.trae.pinguan.web.dto.InstitutionImportRequest;
import com.trae.pinguan.web.dto.InstitutionUpdateRequest;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class InstitutionService {
    private final InstitutionRepository institutionRepository;

    public List<Institution> listAll() {
        return institutionRepository.findAll();
    }
    
    /**
     * 查询机构列表（支持分页和筛选）
     * 
     * @param region 地区筛选
     * @param level 等级筛选
     * @param name 名称搜索（模糊）
     * @param unknownRegionOnly 是否只显示未知地区
     * @param page 页码（从1开始），null表示不分页
     * @param size 每页数量，默认20
     * @return 不分页时返回List，分页时返回PageResult
     */
    public Object listInstitutions(String region, String level, String name, 
                                   Boolean unknownRegionOnly, Integer page, Integer size) {
        // 如果不分页，使用原有逻辑
        if (page == null) {
            return listInstitutionsWithoutPagination(region, level, name, unknownRegionOnly);
        }
        
        // 分页查询
        return listInstitutionsWithPagination(region, level, name, unknownRegionOnly, page, size);
    }
    
    /**
     * 不分页查询
     */
    private List<Institution> listInstitutionsWithoutPagination(String region, String level, 
                                                                String name, Boolean unknownRegionOnly) {
        List<Institution> all = institutionRepository.findAll();
        
        return all.stream()
                .filter(inst -> region == null || region.equals(inst.getRegion()))
                .filter(inst -> level == null || level.equals(inst.getLevel()))
                .filter(inst -> name == null || inst.getName().contains(name))
                .filter(inst -> unknownRegionOnly == null || !unknownRegionOnly || 
                              inst.getRegion() == null || inst.getRegion().trim().isEmpty())
                .collect(Collectors.toList());
    }
    
    /**
     * 分页查询
     */
    private com.trae.pinguan.web.dto.PageResult<Institution> listInstitutionsWithPagination(
            String region, String level, String name, Boolean unknownRegionOnly, 
            Integer page, Integer size) {
        
        // 获取筛选后的数据
        List<Institution> filtered = listInstitutionsWithoutPagination(region, level, name, unknownRegionOnly);
        
        // 参数处理
        int actualPage = page != null && page > 0 ? page : 1;
        int pageSize = size != null && size > 0 ? size : 20;
        
        // 计算分页
        int totalCount = filtered.size();
        int totalPages = (int) Math.ceil((double) totalCount / pageSize);
        int startIndex = (actualPage - 1) * pageSize;
        int endIndex = Math.min(startIndex + pageSize, totalCount);
        
        // 如果页码超出范围，返回空结果
        if (startIndex >= totalCount) {
            return com.trae.pinguan.web.dto.PageResult.<Institution>builder()
                    .content(new java.util.ArrayList<>())
                    .pageNo(actualPage)
                    .pageSize(pageSize)
                    .totalCount((long) totalCount)
                    .totalPages(totalPages)
                    .hasNext(false)
                    .hasPrevious(actualPage > 1)
                    .build();
        }
        
        // 提取当前页数据
        List<Institution> pageData = filtered.subList(startIndex, endIndex);
        
        // 构造分页结果
        return com.trae.pinguan.web.dto.PageResult.<Institution>builder()
                .content(pageData)
                .pageNo(actualPage)
                .pageSize(pageSize)
                .totalCount((long) totalCount)
                .totalPages(totalPages)
                .hasNext(endIndex < totalCount)
                .hasPrevious(actualPage > 1)
                .build();
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
