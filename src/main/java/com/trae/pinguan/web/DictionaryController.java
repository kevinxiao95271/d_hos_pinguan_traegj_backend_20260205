package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.DictionaryItem;
import com.trae.pinguan.service.DictionaryService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.DictionaryItemRequest;
import com.trae.pinguan.web.dto.DictionaryItemUpdateRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

@RestController
@RequestMapping("/api/dictionaries")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "字典管理", description = "字典项管理接口")
public class DictionaryController {
    
    private final DictionaryService dictionaryService;
    
    @GetMapping("/{type}")
    @Operation(summary = "根据类型获取字典项", description = "获取指定类型的所有启用字典项")
    public ApiResponse<List<DictionaryItem>> getByType(
            @Parameter(description = "字典类型", example = "subject_type")
            @PathVariable String type) {
        log.info("获取字典项: type={}", type);
        List<DictionaryItem> items = dictionaryService.getByType(type);
        return ApiResponse.ok(items);
    }
    
    @GetMapping
    @Operation(summary = "获取所有启用的字典项")
    public ApiResponse<List<DictionaryItem>> getAllActive() {
        log.info("获取所有启用的字典项");
        List<DictionaryItem> items = dictionaryService.getAllActive();
        return ApiResponse.ok(items);
    }
    
    @PostMapping
    @Operation(summary = "创建字典项")
    public ApiResponse<DictionaryItem> create(@Valid @RequestBody DictionaryItemRequest request) {
        log.info("创建字典项: {}", request);
        DictionaryItem item = dictionaryService.create(request);
        return ApiResponse.ok(item);
    }
    
    @PutMapping("/{id}")
    @Operation(summary = "更新字典项")
    public ApiResponse<DictionaryItem> update(
            @Parameter(description = "字典项ID")
            @PathVariable Long id,
            @Valid @RequestBody DictionaryItemUpdateRequest request) {
        log.info("更新字典项: id={}, request={}", id, request);
        DictionaryItem item = dictionaryService.update(id, request);
        return ApiResponse.ok(item);
    }
    
    @DeleteMapping("/{id}")
    @Operation(summary = "删除字典项", description = "逻辑删除，将active设置为false")
    public ApiResponse<Void> delete(
            @Parameter(description = "字典项ID")
            @PathVariable Long id) {
        log.info("删除字典项: id={}", id);
        dictionaryService.delete(id);
        return ApiResponse.ok(null);
    }
}
