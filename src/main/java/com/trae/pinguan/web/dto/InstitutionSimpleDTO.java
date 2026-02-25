package com.trae.pinguan.web.dto;

import com.trae.pinguan.domain.entity.Institution;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "机构简要信息（用于下拉选择）")
public class InstitutionSimpleDTO {
    
    @Schema(description = "机构ID")
    private Long id;
    
    @Schema(description = "机构名称")
    private String name;
    
    @Schema(description = "地区")
    private String region;
    
    @Schema(description = "等级")
    private String level;
    
    @Schema(description = "USCC（后4位）")
    private String usccLast4;
    
    @Schema(description = "显示文本（用于前端显示）")
    private String displayText;
    
    public static InstitutionSimpleDTO from(Institution institution) {
        String uscc = institution.getUscc();
        String usccLast4 = uscc != null && uscc.length() >= 4 
            ? uscc.substring(uscc.length() - 4) 
            : "";
        
        String displayText = institution.getName();
        if (institution.getRegion() != null) {
            displayText += " (" + institution.getRegion() + ")";
        }
        if (institution.getLevel() != null && !"未定等".equals(institution.getLevel())) {
            displayText += " [" + institution.getLevel() + "]";
        }
        
        return InstitutionSimpleDTO.builder()
                .id(institution.getId())
                .name(institution.getName())
                .region(institution.getRegion())
                .level(institution.getLevel())
                .usccLast4(usccLast4)
                .displayText(displayText)
                .build();
    }
}
