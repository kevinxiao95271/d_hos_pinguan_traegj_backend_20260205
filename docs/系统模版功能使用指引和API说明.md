# 系统模版功能使用指引和 API 说明

## 📋 目录

1. [场景一：用户注册流程（下载模版 + 上传文件）](#场景一用户注册流程)
2. [场景二：管理后台查看项目列表（直接预览文件）](#场景二管理后台查看项目列表)
3. [场景三：OPS 管理模版](#场景三ops-管理模版)
4. [API 新增与调整说明](#api-新增与调整说明)
5. [前端集成示例](#前端集成示例)

---

## 场景一：用户注册流程

### 业务流程

```
Step 1: 用户注册完成 
   ↓
Step 2: 下载系统模版（报名表模版 + 成果报告说明）
   ↓
Step 3: 填写模版文件
   ↓
Step 4: 上传填写好的文件（报名材料）
   ↓
Step 5: 提交报名
```

### API 调用流程

#### 1. 用户注册
**API**: `POST /api/auth/register`

**请求示例**:
```json
{
  "phone": "13800138000",
  "password": "password123",
  "name": "张三",
  "title": "科室主任",
  "role": "CONTESTANT",
  "institutionId": 123
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "userId": 456,
    "name": "张三",
    "token": "eyJhbGciOiJIUzI1NiJ9..."
  }
}
```

---

#### 2. 下载系统模版（公开接口，无需 token）

##### 2.1 获取模版列表
**API**: `GET /api/system-templates/active`

**特点**: 
- ✅ **无需 JWT token**（公开接口）
- ✅ 永久有效的 URL

**请求示例**:
```bash
curl -X GET http://localhost:6031/api/system-templates/active
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "templateType": "registration_form",
      "fileName": "2026浙江省医院品管大赛报名表模板.docx",
      "fileSize": 16967,
      "version": 1,
      "isActive": true,
      "uploadedBy": null,
      "uploadedAt": "2026-02-27T16:00:00",
      "description": null
    },
    {
      "id": 2,
      "templateType": "result_report",
      "fileName": "成果报告相关说明.docx",
      "fileSize": 17671,
      "version": 1,
      "isActive": true,
      "uploadedBy": null,
      "uploadedAt": "2026-02-27T16:00:00",
      "description": null
    }
  ]
}
```

##### 2.2 下载模版文件
**API**: `GET /api/system-templates/{id}/download`

**特点**:
- ✅ **无需 JWT token**（公开接口）
- ✅ **URL 永久有效**
- ✅ 后端流式下载，支持最大 30MB 文件
- ✅ 中文文件名自动编码

**请求示例**:
```bash
# 下载报名表模版
curl -X GET http://localhost:6031/api/system-templates/1/download \
  -o 报名表模版.docx

# 下载成果报告说明
curl -X GET http://localhost:6031/api/system-templates/2/download \
  -o 成果报告说明.docx
```

---

#### 3. 上传填写好的文件（报名材料）

**API**: `POST /api/registrations/{id}/materials`

**权限**: 需要 JWT token（CONTESTANT）

**请求示例**:
```bash
curl -X POST http://localhost:6031/api/registrations/123/materials \
  -H "Authorization: Bearer {TOKEN}" \
  -F "type=registration_form" \
  -F "file=@填写好的报名表.docx"
```

**参数说明**:
- `{id}`: 报名记录 ID（创建报名后获得）
- `type`: 材料类型
  - `registration_form` - 报名表
  - `result_report` - 成果报告
  - `supporting_materials` - 支撑材料（可多个）

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 789,
    "type": "registration_form",
    "fileName": "填写好的报名表.docx",
    "fileUrl": "registration-files/123/uuid-填写好的报名表.docx",
    "uploadedAt": "2026-02-27T17:00:00"
  }
}
```

---

#### 4. 查看已上传的材料列表

**API**: `GET /api/registrations/{id}/materials`

**权限**: 需要 JWT token

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 789,
      "type": "registration_form",
      "fileName": "填写好的报名表.docx",
      "fileUrl": "registration-files/123/uuid-填写好的报名表.docx",
      "uploadedAt": "2026-02-27T17:00:00"
    },
    {
      "id": 790,
      "type": "supporting_materials",
      "fileName": "支撑材料1.pdf",
      "fileUrl": "registration-files/123/uuid-支撑材料1.pdf",
      "uploadedAt": "2026-02-27T17:05:00"
    }
  ]
}
```

---

### 前端集成示例

#### 注册成功页（下载模版）

```vue
<template>
  <div class="registration-success">
    <h2>✅ 注册成功！</h2>
    <p>您可以下载以下模版文件，填写后提交报名：</p>
    
    <div class="template-list">
      <div 
        v-for="template in templates" 
        :key="template.id"
        class="template-card"
      >
        <div class="template-icon">📄</div>
        <div class="template-info">
          <h4>{{ template.fileName }}</h4>
          <p>文件大小: {{ formatFileSize(template.fileSize) }}</p>
          <p>版本: v{{ template.version }}</p>
        </div>
        <button @click="downloadTemplate(template.id, template.fileName)">
          下载模版
        </button>
      </div>
    </div>
    
    <button @click="goToRegistration" class="primary-button">
      开始填写报名信息
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      templates: []
    }
  },
  
  async mounted() {
    // 获取模版列表（无需 token）
    const response = await axios.get('/api/system-templates/active')
    this.templates = response.data.data
  },
  
  methods: {
    downloadTemplate(templateId, fileName) {
      // 方式1：直接下载
      window.location.href = `/api/system-templates/${templateId}/download`
      
      // 方式2：使用 axios 下载（更好的用户体验）
      axios.get(`/api/system-templates/${templateId}/download`, {
        responseType: 'blob'
      }).then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', fileName)
        document.body.appendChild(link)
        link.click()
        link.remove()
      })
    },
    
    formatFileSize(bytes) {
      return (bytes / 1024).toFixed(2) + ' KB'
    },
    
    goToRegistration() {
      this.$router.push('/registration/create')
    }
  }
}
</script>
```

#### 报名页（上传文件）

```vue
<template>
  <div class="registration-form">
    <h3>上传报名材料</h3>
    
    <!-- 报名表上传 -->
    <div class="upload-section">
      <label>报名表 <span class="required">*</span></label>
      <input 
        type="file" 
        accept=".docx,.doc"
        @change="handleFileUpload($event, 'registration_form')"
      />
      <div v-if="uploadedFiles.registration_form" class="file-preview">
        ✅ {{ uploadedFiles.registration_form.fileName }}
      </div>
    </div>
    
    <!-- 成果报告上传 -->
    <div class="upload-section">
      <label>成果报告</label>
      <input 
        type="file" 
        accept=".docx,.doc,.pdf"
        @change="handleFileUpload($event, 'result_report')"
      />
      <div v-if="uploadedFiles.result_report" class="file-preview">
        ✅ {{ uploadedFiles.result_report.fileName }}
      </div>
    </div>
    
    <!-- 支撑材料上传（可多个）-->
    <div class="upload-section">
      <label>支撑材料（可多个）</label>
      <input 
        type="file" 
        accept=".pdf,.docx,.xlsx,.jpg,.png"
        multiple
        @change="handleMultipleFileUpload($event, 'supporting_materials')"
      />
      <div v-for="file in uploadedFiles.supporting_materials" :key="file.id" class="file-preview">
        ✅ {{ file.fileName }}
      </div>
    </div>
    
    <button @click="submit" class="submit-button">提交报名</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      registrationId: null,
      uploadedFiles: {
        registration_form: null,
        result_report: null,
        supporting_materials: []
      }
    }
  },
  
  methods: {
    async handleFileUpload(event, type) {
      const file = event.target.files[0]
      if (!file) return
      
      const formData = new FormData()
      formData.append('type', type)
      formData.append('file', file)
      
      try {
        const response = await axios.post(
          `/api/registrations/${this.registrationId}/materials`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Authorization': `Bearer ${this.$store.state.token}`
            }
          }
        )
        
        this.uploadedFiles[type] = response.data.data
        this.$message.success('上传成功')
      } catch (error) {
        this.$message.error('上传失败')
      }
    },
    
    async handleMultipleFileUpload(event, type) {
      const files = Array.from(event.target.files)
      
      for (const file of files) {
        const formData = new FormData()
        formData.append('type', type)
        formData.append('file', file)
        
        const response = await axios.post(
          `/api/registrations/${this.registrationId}/materials`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Authorization': `Bearer ${this.$store.state.token}`
            }
          }
        )
        
        this.uploadedFiles.supporting_materials.push(response.data.data)
      }
    },
    
    async submit() {
      // 提交报名
      await axios.post(`/api/registrations/${this.registrationId}/submit`, {}, {
        headers: { 'Authorization': `Bearer ${this.$store.state.token}` }
      })
      
      this.$message.success('报名提交成功')
      this.$router.push('/my-registrations')
    }
  }
}
</script>
```

---

## 场景二：管理后台查看项目列表

### 需求

管理后台（OPS 和 组委会）查看项目列表时：
- 每一行数据直接显示"文件预览"按钮
- 无需进入详情页即可下载/预览文件
- 支持多个文件类型（报名表、成果报告、支撑材料）

### 当前问题

**当前的 `RegistrationFilterItem` DTO** 不包含材料文件信息，只有基本项目信息：

```java
public class RegistrationFilterItem {
    private Long registrationId;
    private String projectName;
    private String institutionName;
    private String institutionLevel;
    private GroupType groupType;
    private String groupCode;
    private LocalDateTime submittedAt;
    private String subjectTypeCode;
    private String methodCode;
    private String applicantName;
    // ❌ 缺少：材料文件列表
}
```

### 解决方案：扩展 DTO 和查询

#### 选项 A：在列表查询中关联查询材料文件（推荐）

**优点**:
- 一次查询获取所有数据
- 前端无需额外请求
- 性能较好（使用 JOIN）

**缺点**:
- 需要修改现有的 Repository 查询
- 数据量稍大（但可接受）

**实施方案**:

1. **新增 DTO 字段**:

```java
// RegistrationFilterItem.java
public class RegistrationFilterItem {
    // ... 现有字段
    
    // 新增：材料文件列表（简化版）
    private List<MaterialFileSimple> materials;
    
    @Data
    @AllArgsConstructor
    public static class MaterialFileSimple {
        private Long id;
        private String type;
        private String fileName;
        private String downloadUrl;  // 预构建的下载 URL
    }
}
```

2. **修改 Repository 查询**（使用 LEFT JOIN）:

```java
// RegistrationRepository.java
@Query("SELECT DISTINCT new com.trae.pinguan.web.dto.RegistrationFilterItem(" +
       "r.id, r.projectName, i.name, i.level, r.groupType, r.groupCode, " +
       "r.submittedAt, a.subjectTypeCode, a.methodCode, '', '', r.applicant.name) " +
       "FROM Registration r " +
       "LEFT JOIN r.institution i " +
       "LEFT JOIN r.activityInfo a " +
       // ❌ 不能在这里 JOIN MaterialFile，会导致数据重复
       "WHERE ... ")
List<RegistrationFilterItem> filterRegistrations(...);
```

**问题**: JPA 无法在一个查询中同时返回实体和集合。

**最佳实践**: 分两步查询

```java
// RegistrationService.java
public List<RegistrationFilterItem> filterRegistrations(...) {
    // Step 1: 查询基本信息
    List<RegistrationFilterItem> items = repository.filterRegistrations(...);
    
    // Step 2: 批量查询材料文件
    List<Long> registrationIds = items.stream()
        .map(RegistrationFilterItem::getRegistrationId)
        .collect(Collectors.toList());
    
    Map<Long, List<MaterialFile>> materialsMap = materialFileRepository
        .findByRegistrationIdIn(registrationIds)
        .stream()
        .collect(Collectors.groupingBy(m -> m.getRegistration().getId()));
    
    // Step 3: 组装数据
    for (RegistrationFilterItem item : items) {
        List<MaterialFile> materials = materialsMap.getOrDefault(item.getRegistrationId(), List.of());
        item.setMaterials(
            materials.stream()
                .map(m -> new MaterialFileSimple(
                    m.getId(),
                    m.getType(),
                    m.getFileName(),
                    "/api/materials/" + m.getId() + "/download"  // 构建下载 URL
                ))
                .collect(Collectors.toList())
        );
    }
    
    return items;
}
```

3. **新增材料下载 API**:

```java
// MaterialController.java
@GetMapping("/{id}/download")
@Operation(summary = "下载材料文件")
public ResponseEntity<InputStreamResource> download(@PathVariable Long id) {
    MaterialFile material = materialService.getById(id);
    
    // 从 MinIO 获取文件流
    String bucketName = minioProperties.getBucket().getRegistrationFiles();
    InputStream inputStream = fileStorageService.getInputStream(
        material.getFileUrl(), bucketName
    );
    
    // 文件名编码
    String encodedFilename;
    try {
        encodedFilename = URLEncoder.encode(material.getFileName(), "UTF-8")
            .replace("+", "%20");
    } catch (UnsupportedEncodingException e) {
        throw new IllegalStateException("UTF-8 encoding not supported", e);
    }
    
    return ResponseEntity.ok()
        .contentType(MediaType.APPLICATION_OCTET_STREAM)
        .header(HttpHeaders.CONTENT_DISPOSITION, 
                "attachment; filename*=UTF-8''" + encodedFilename)
        .body(new InputStreamResource(inputStream));
}
```

4. **JWT 白名单更新**（如果需要公开下载）:

```java
// JwtAuthorizationFilter.java
// 在 doFilterInternal 方法中添加
if ("GET".equalsIgnoreCase(method) && 
    path.matches("^/api/materials/\\d+/download$")) {
    // 根据需求决定是否公开
    // 选项1: 公开下载（无需 token）
    filterChain.doFilter(request, response);
    return;
    
    // 选项2: 需要 token（默认行为，不添加白名单）
}
```

---

#### 选项 B：前端按需加载（不推荐）

前端在渲染列表时，对每一行单独请求材料文件列表。

**缺点**:
- 产生 N 次额外请求（N = 列表行数）
- 性能差
- 用户体验不好（加载时间长）

---

### 前端集成示例（列表页）

```vue
<template>
  <div class="registration-list">
    <el-table :data="registrations" stripe>
      <el-table-column prop="projectName" label="项目名称" width="200" />
      <el-table-column prop="institutionName" label="医院名称" width="200" />
      <el-table-column prop="applicantName" label="申请人" width="100" />
      <el-table-column prop="submittedAt" label="提交时间" width="150" />
      
      <!-- 文件预览列 -->
      <el-table-column label="材料文件" width="300">
        <template slot-scope="scope">
          <div v-if="scope.row.materials && scope.row.materials.length > 0">
            <el-tag 
              v-for="material in scope.row.materials" 
              :key="material.id"
              size="small"
              style="margin: 2px; cursor: pointer"
              @click="downloadMaterial(material)"
            >
              {{ getMaterialTypeLabel(material.type) }}
            </el-tag>
          </div>
          <span v-else style="color: #ccc">暂无文件</span>
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-button size="small" @click="viewDetail(scope.row.registrationId)">
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      registrations: []
    }
  },
  
  async mounted() {
    // 获取项目列表（已包含材料文件）
    const response = await axios.get('/api/admin/registrations/filter', {
      params: {
        competitionId: this.$route.query.competitionId,
        status: 'SUBMITTED'
      },
      headers: {
        'Authorization': `Bearer ${this.$store.state.token}`
      }
    })
    
    this.registrations = response.data.data
  },
  
  methods: {
    downloadMaterial(material) {
      // 直接下载文件
      window.open(material.downloadUrl, '_blank')
      
      // 或者使用 axios 下载
      axios.get(material.downloadUrl, {
        responseType: 'blob',
        headers: { 'Authorization': `Bearer ${this.$store.state.token}` }
      }).then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', material.fileName)
        document.body.appendChild(link)
        link.click()
        link.remove()
      })
    },
    
    getMaterialTypeLabel(type) {
      const labels = {
        'registration_form': '报名表',
        'result_report': '成果报告',
        'supporting_materials': '支撑材料'
      }
      return labels[type] || type
    },
    
    viewDetail(registrationId) {
      this.$router.push(`/registration/${registrationId}`)
    }
  }
}
</script>

<style scoped>
.el-tag {
  transition: all 0.3s;
}

.el-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
</style>
```

---

## 场景三：OPS 管理模版

### 业务流程

```
OPS 登录后台 
   ↓
进入"系统管理" → "模版管理"
   ↓
查看当前激活模版（报名表 v2、成果报告 v1）
   ↓
上传新版本模版（自动停用旧版本）
   ↓
查看历史版本
   ↓
（可选）删除无用的历史版本
```

### API 调用流程

#### 1. 查看当前激活模版

**API**: `GET /api/system-templates/active`

**权限**: OPS（但实际上该接口是公开的，任何人都可以查看）

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 3,
      "templateType": "registration_form",
      "fileName": "2026浙江省医院品管大赛报名表模板_v2.docx",
      "fileSize": 18500,
      "version": 2,
      "isActive": true,
      "uploadedBy": "管理员",
      "uploadedAt": "2026-02-28T10:00:00",
      "description": "更新了评分标准"
    },
    {
      "id": 2,
      "templateType": "result_report",
      "fileName": "成果报告相关说明.docx",
      "fileSize": 17671,
      "version": 1,
      "isActive": true,
      "uploadedBy": null,
      "uploadedAt": "2026-02-27T16:00:00",
      "description": null
    }
  ]
}
```

---

#### 2. 上传新版本模版

**API**: `POST /api/system-templates/upload`

**权限**: **仅 OPS**

**请求示例**:
```bash
curl -X POST http://localhost:6031/api/system-templates/upload \
  -H "Authorization: Bearer {OPS_TOKEN}" \
  -F "templateType=registration_form" \
  -F "description=更新了评分标准，增加了创新性指标" \
  -F "file=@报名表模版_v3.docx"
```

**参数说明**:
- `templateType`: 模版类型（必填）
  - `registration_form` - 报名表模版
  - `result_report` - 成果报告说明
- `description`: 版本说明（可选）
- `file`: 模版文件（必填）

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 4,
    "templateType": "registration_form",
    "fileName": "报名表模版_v3.docx",
    "fileSize": 19200,
    "version": 3,
    "isActive": true,
    "uploadedBy": "管理员",
    "uploadedAt": "2026-03-01T14:30:00",
    "description": "更新了评分标准，增加了创新性指标"
  }
}
```

**自动处理**:
- ✅ 版本号自动递增（v3）
- ✅ 旧版本自动设为非激活（v1, v2 的 `isActive` → `false`）
- ✅ 新版本设为激活（v3 的 `isActive` → `true`）

---

#### 3. 查看历史版本

**API**: `GET /api/system-templates/history/{templateType}`

**权限**: **仅 OPS**

**请求示例**:
```bash
curl -X GET http://localhost:6031/api/system-templates/history/registration_form \
  -H "Authorization: Bearer {OPS_TOKEN}"
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 4,
      "templateType": "registration_form",
      "fileName": "报名表模版_v3.docx",
      "fileSize": 19200,
      "version": 3,
      "isActive": true,
      "uploadedBy": "管理员",
      "uploadedAt": "2026-03-01T14:30:00",
      "description": "更新了评分标准，增加了创新性指标"
    },
    {
      "id": 3,
      "templateType": "registration_form",
      "fileName": "2026浙江省医院品管大赛报名表模板_v2.docx",
      "fileSize": 18500,
      "version": 2,
      "isActive": false,
      "uploadedBy": "管理员",
      "uploadedAt": "2026-02-28T10:00:00",
      "description": "更新了评分标准"
    },
    {
      "id": 1,
      "templateType": "registration_form",
      "fileName": "2026浙江省医院品管大赛报名表模板.docx",
      "fileSize": 16967,
      "version": 1,
      "isActive": false,
      "uploadedBy": null,
      "uploadedAt": "2026-02-27T16:00:00",
      "description": null
    }
  ]
}
```

---

#### 4. 删除历史版本（谨慎操作）

**API**: `DELETE /api/system-templates/{id}`

**权限**: **仅 OPS**

**请求示例**:
```bash
curl -X DELETE http://localhost:6031/api/system-templates/1 \
  -H "Authorization: Bearer {OPS_TOKEN}"
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

**注意事项**:
- ⚠️ 删除会同时删除 MinIO 中的文件和数据库记录
- ⚠️ 建议只删除非激活的旧版本
- ⚠️ 如果误删激活版本，需要重新上传

---

### 前端集成示例（OPS 后台）

```vue
<template>
  <div class="template-management">
    <h2>系统模版管理</h2>
    
    <!-- 当前激活模版 -->
    <el-card class="active-templates">
      <div slot="header">
        <span>当前激活模版</span>
      </div>
      
      <el-table :data="activeTemplates" stripe>
        <el-table-column prop="templateType" label="类型" width="150">
          <template slot-scope="scope">
            {{ getTemplateTypeLabel(scope.row.templateType) }}
          </template>
        </el-table-column>
        <el-table-column prop="fileName" label="文件名" width="300" />
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="uploadedBy" label="上传人" width="100" />
        <el-table-column prop="uploadedAt" label="上传时间" width="180" />
        <el-table-column label="操作" width="200">
          <template slot-scope="scope">
            <el-button size="small" @click="downloadTemplate(scope.row.id, scope.row.fileName)">
              下载
            </el-button>
            <el-button size="small" type="primary" @click="showUploadDialog(scope.row.templateType)">
              更新版本
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 上传新版本对话框 -->
    <el-dialog :visible.sync="uploadDialogVisible" title="上传新版本模版" width="500px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="模版类型">
          <el-select v-model="uploadForm.templateType" disabled>
            <el-option label="报名表模版" value="registration_form" />
            <el-option label="成果报告说明" value="result_report" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="版本说明">
          <el-input 
            v-model="uploadForm.description" 
            type="textarea" 
            placeholder="请输入版本更新说明（可选）"
          />
        </el-form-item>
        
        <el-form-item label="选择文件">
          <el-upload
            ref="upload"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            accept=".docx,.doc"
          >
            <el-button size="small" type="primary">选择文件</el-button>
            <div slot="tip" class="el-upload__tip">
              仅支持 .docx 或 .doc 文件，最大 30MB
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <div slot="footer">
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="uploadNewVersion" :loading="uploading">
          确认上传
        </el-button>
      </div>
    </el-dialog>
    
    <!-- 历史版本 -->
    <el-card class="history-templates" style="margin-top: 20px">
      <div slot="header">
        <span>历史版本</span>
        <el-select 
          v-model="selectedTemplateType" 
          placeholder="选择模版类型"
          style="margin-left: 20px; width: 200px"
          @change="loadHistory"
        >
          <el-option label="报名表模版" value="registration_form" />
          <el-option label="成果报告说明" value="result_report" />
        </el-select>
      </div>
      
      <el-table :data="historyTemplates" stripe>
        <el-table-column prop="fileName" label="文件名" width="300" />
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="isActive" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.isActive ? 'success' : 'info'">
              {{ scope.row.isActive ? '激活' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="版本说明" width="250" show-overflow-tooltip />
        <el-table-column prop="uploadedAt" label="上传时间" width="180" />
        <el-table-column label="操作" width="150">
          <template slot-scope="scope">
            <el-button size="small" @click="downloadTemplate(scope.row.id, scope.row.fileName)">
              下载
            </el-button>
            <el-button 
              v-if="!scope.row.isActive"
              size="small" 
              type="danger" 
              @click="deleteTemplate(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeTemplates: [],
      historyTemplates: [],
      selectedTemplateType: 'registration_form',
      uploadDialogVisible: false,
      uploading: false,
      uploadForm: {
        templateType: '',
        description: '',
        file: null
      }
    }
  },
  
  async mounted() {
    await this.loadActiveTemplates()
    await this.loadHistory()
  },
  
  methods: {
    async loadActiveTemplates() {
      const response = await axios.get('/api/system-templates/active', {
        headers: { 'Authorization': `Bearer ${this.$store.state.token}` }
      })
      this.activeTemplates = response.data.data
    },
    
    async loadHistory() {
      if (!this.selectedTemplateType) return
      
      const response = await axios.get(
        `/api/system-templates/history/${this.selectedTemplateType}`,
        {
          headers: { 'Authorization': `Bearer ${this.$store.state.token}` }
        }
      )
      this.historyTemplates = response.data.data
    },
    
    downloadTemplate(templateId, fileName) {
      window.open(`/api/system-templates/${templateId}/download`, '_blank')
    },
    
    showUploadDialog(templateType) {
      this.uploadForm.templateType = templateType
      this.uploadForm.description = ''
      this.uploadForm.file = null
      this.uploadDialogVisible = true
    },
    
    handleFileChange(file, fileList) {
      this.uploadForm.file = file.raw
    },
    
    async uploadNewVersion() {
      if (!this.uploadForm.file) {
        this.$message.warning('请选择文件')
        return
      }
      
      const formData = new FormData()
      formData.append('templateType', this.uploadForm.templateType)
      formData.append('description', this.uploadForm.description || '')
      formData.append('file', this.uploadForm.file)
      
      this.uploading = true
      try {
        await axios.post('/api/system-templates/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${this.$store.state.token}`
          }
        })
        
        this.$message.success('上传成功！旧版本已自动停用')
        this.uploadDialogVisible = false
        await this.loadActiveTemplates()
        await this.loadHistory()
      } catch (error) {
        this.$message.error('上传失败：' + (error.response?.data?.message || '未知错误'))
      } finally {
        this.uploading = false
      }
    },
    
    async deleteTemplate(templateId) {
      await this.$confirm('确定删除此模版？删除后无法恢复', '警告', {
        type: 'warning'
      })
      
      try {
        await axios.delete(`/api/system-templates/${templateId}`, {
          headers: { 'Authorization': `Bearer ${this.$store.state.token}` }
        })
        
        this.$message.success('删除成功')
        await this.loadHistory()
      } catch (error) {
        this.$message.error('删除失败：' + (error.response?.data?.message || '未知错误'))
      }
    },
    
    getTemplateTypeLabel(type) {
      const labels = {
        'registration_form': '报名表模版',
        'result_report': '成果报告说明'
      }
      return labels[type] || type
    }
  }
}
</script>

<style scoped>
.template-management {
  padding: 20px;
}

.el-card {
  margin-bottom: 20px;
}

.el-tag {
  font-weight: bold;
}
</style>
```

---

## API 新增与调整说明

### 新增 API（系统模版）

| API | 方法 | 权限 | 说明 |
|-----|------|------|------|
| `/api/system-templates/active` | GET | **公开** | 获取激活模版列表 |
| `/api/system-templates/{id}/download` | GET | **公开** | 下载模版文件（URL永久有效） |
| `/api/system-templates/upload` | POST | **仅 OPS** | 上传新版本模版 |
| `/api/system-templates/history/{type}` | GET | **仅 OPS** | 查看历史版本 |
| `/api/system-templates/{id}` | DELETE | **仅 OPS** | 删除模版 |

### 需要调整的 API（报名材料）

#### 1. 扩展列表查询 DTO

**文件**: `src/main/java/com/trae/pinguan/web/dto/RegistrationFilterItem.java`

**新增字段**:
```java
// 新增：材料文件列表
private List<MaterialFileSimple> materials;

@Data
@AllArgsConstructor
public static class MaterialFileSimple {
    private Long id;
    private String type;
    private String fileName;
    private String downloadUrl;
}
```

#### 2. 新增材料文件 Repository 方法

**文件**: `src/main/java/com/trae/pinguan/repository/MaterialFileRepository.java`

**新增方法**:
```java
/**
 * 批量查询多个报名的材料文件
 */
List<MaterialFile> findByRegistrationIdIn(List<Long> registrationIds);
```

#### 3. 修改 Service 查询逻辑

**文件**: `src/main/java/com/trae/pinguan/service/RegistrationService.java`

**修改 `filterRegistrations` 方法**:
```java
public List<RegistrationFilterItem> filterRegistrations(...) {
    // Step 1: 查询基本信息
    List<RegistrationFilterItem> items = repository.filterRegistrations(...);
    
    // Step 2: 批量查询材料文件
    List<Long> registrationIds = items.stream()
        .map(RegistrationFilterItem::getRegistrationId)
        .collect(Collectors.toList());
    
    if (!registrationIds.isEmpty()) {
        Map<Long, List<MaterialFile>> materialsMap = materialFileRepository
            .findByRegistrationIdIn(registrationIds)
            .stream()
            .collect(Collectors.groupingBy(m -> m.getRegistration().getId()));
        
        // Step 3: 组装数据
        for (RegistrationFilterItem item : items) {
            List<MaterialFile> materials = materialsMap.getOrDefault(
                item.getRegistrationId(), List.of()
            );
            item.setMaterials(
                materials.stream()
                    .map(m -> new RegistrationFilterItem.MaterialFileSimple(
                        m.getId(),
                        m.getType(),
                        m.getFileName(),
                        "/api/materials/" + m.getId() + "/download"
                    ))
                    .collect(Collectors.toList())
            );
        }
    }
    
    return items;
}
```

#### 4. 新增材料下载 API

**文件**: `src/main/java/com/trae/pinguan/web/MaterialController.java`

**新增方法**:
```java
@GetMapping("/{id}/download")
@Operation(summary = "下载材料文件")
public ResponseEntity<InputStreamResource> download(@PathVariable Long id) {
    MaterialFile material = materialService.getById(id);
    
    // 权限检查（可选）
    // - CONTESTANT 只能下载自己的
    // - OPS/COMMITTEE 可以下载所有的
    
    String bucketName = minioProperties.getBucket().getRegistrationFiles();
    InputStream inputStream = fileStorageService.getInputStream(
        material.getFileUrl(), bucketName
    );
    
    String encodedFilename;
    try {
        encodedFilename = URLEncoder.encode(material.getFileName(), "UTF-8")
            .replace("+", "%20");
    } catch (UnsupportedEncodingException e) {
        throw new IllegalStateException("UTF-8 encoding not supported", e);
    }
    
    return ResponseEntity.ok()
        .contentType(MediaType.APPLICATION_OCTET_STREAM)
        .header(HttpHeaders.CONTENT_DISPOSITION, 
                "attachment; filename*=UTF-8''" + encodedFilename)
        .body(new InputStreamResource(inputStream));
}
```

#### 5. JWT 白名单（根据需求）

**选项 A**: 材料文件公开下载（不推荐）
```java
// JwtAuthorizationFilter.java
if ("GET".equalsIgnoreCase(method) && 
    path.matches("^/api/materials/\\d+/download$")) {
    filterChain.doFilter(request, response);
    return;
}
```

**选项 B**: 需要 token（推荐）
- 不添加白名单，保持默认行为
- OPS/COMMITTEE/CONTESTANT 需要 token 才能下载
- Controller 中可以添加权限检查逻辑

---

## 总结

### 已完成 ✅
1. ✅ 系统模版功能完全实现（MinIO 版）
2. ✅ 2个模版文件已上传到 MinIO
3. ✅ 数据库表创建成功
4. ✅ API 端点全部可用
5. ✅ JWT 白名单已配置（模版下载公开）
6. ✅ 编译成功

### 待实施 ⏳
1. ⏳ 扩展 `RegistrationFilterItem` DTO（增加材料文件字段）
2. ⏳ 修改 `RegistrationService.filterRegistrations` 方法（关联查询材料）
3. ⏳ 新增 `MaterialController.download` 方法（材料下载 API）
4. ⏳ 新增 `MaterialFileRepository.findByRegistrationIdIn` 方法
5. ⏳ （可选）JWT 白名单更新（材料下载权限）

### 下一步建议
1. 先实施"扩展列表查询"功能（步骤 1-4）
2. 测试管理后台列表页的文件预览功能
3. 根据业务需求决定材料下载权限策略
4. 编译、部署、集成测试

---

**文档版本**: v1.0  
**编写日期**: 2026-02-27  
**编写人**: AI Assistant
