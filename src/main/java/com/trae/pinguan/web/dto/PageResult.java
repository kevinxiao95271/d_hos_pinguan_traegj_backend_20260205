package com.trae.pinguan.web.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.domain.Page;

import java.util.List;

/**
 * 分页结果DTO
 * 
 * 页码规范：从1开始（第1页、第2页...），无第0页
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PageResult<T> {
    /**
     * 数据列表
     */
    private List<T> content;
    
    /**
     * 当前页码（从1开始）
     */
    private Integer pageNo;
    
    /**
     * 每页数量
     */
    private Integer pageSize;
    
    /**
     * 总记录数
     */
    private Long totalCount;
    
    /**
     * 总页数
     */
    private Integer totalPages;
    
    /**
     * 是否有下一页
     */
    private Boolean hasNext;
    
    /**
     * 是否有上一页
     */
    private Boolean hasPrevious;
    
    /**
     * 从Spring Data的Page对象转换
     * 注意：Spring Data的页码从0开始，需要转换为从1开始
     * 
     * @param springPage Spring Data的分页对象
     * @return PageResult对象（页码从1开始）
     */
    public static <T> PageResult<T> of(Page<T> springPage) {
        return PageResult.<T>builder()
                .content(springPage.getContent())
                .pageNo(springPage.getNumber() + 1)  // 转换：0-based -> 1-based
                .pageSize(springPage.getSize())
                .totalCount(springPage.getTotalElements())
                .totalPages(springPage.getTotalPages())
                .hasNext(springPage.hasNext())
                .hasPrevious(springPage.hasPrevious())
                .build();
    }
}
