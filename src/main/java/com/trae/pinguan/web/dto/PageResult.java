package com.trae.pinguan.web.dto;

import java.util.List;
import lombok.Data;
import org.springframework.data.domain.Page;

@Data
public class PageResult<T> {
    private List<T> content;
    private long totalElements;
    private int totalPages;
    private int pageNo;
    private int size;

    public static <T> PageResult<T> of(Page<T> page) {
        PageResult<T> result = new PageResult<>();
        result.content = page.getContent();
        result.totalElements = page.getTotalElements();
        result.totalPages = page.getTotalPages();
        result.pageNo = page.getNumber() + 1;
        result.size = page.getSize();
        return result;
    }
}
