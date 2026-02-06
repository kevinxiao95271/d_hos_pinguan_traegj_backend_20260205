package com.trae.pinguan.web;

import com.trae.pinguan.domain.entity.DictionaryItem;
import com.trae.pinguan.service.DictionaryService;
import com.trae.pinguan.web.dto.ApiResponse;
import com.trae.pinguan.web.dto.DictionaryItemRequest;
import com.trae.pinguan.web.dto.DictionaryItemUpdateRequest;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.util.List;
import javax.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/dictionaries")
@RequiredArgsConstructor
@Tag(name = "字典")
@SecurityRequirement(name = "BearerAuth")
public class DictionaryController {
    private final DictionaryService dictionaryService;

    @GetMapping("/{type}")
    @Operation(summary = "按类型获取字典项")
    public ApiResponse<List<DictionaryItem>> list(@PathVariable String type) {
        return ApiResponse.ok(dictionaryService.listByType(type));
    }

    @GetMapping
    @Operation(summary = "字典项列表")
    public ApiResponse<List<DictionaryItem>> listAll() {
        return ApiResponse.ok(dictionaryService.listAll());
    }

    @PostMapping
    @Operation(summary = "新增字典项")
    public ApiResponse<DictionaryItem> create(@Valid @RequestBody DictionaryItemRequest request) {
        return ApiResponse.ok(dictionaryService.create(request));
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新字典项")
    public ApiResponse<DictionaryItem> update(@PathVariable Long id,
                                              @Valid @RequestBody DictionaryItemUpdateRequest request) {
        return ApiResponse.ok(dictionaryService.update(id, request));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除字典项")
    public ApiResponse<Void> delete(@PathVariable Long id) {
        dictionaryService.delete(id);
        return ApiResponse.ok(null);
    }
}
