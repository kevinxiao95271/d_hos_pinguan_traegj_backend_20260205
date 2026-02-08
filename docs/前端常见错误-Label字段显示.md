# 前端常见错误 - Label字段显示

## ❌ 问题描述

前端页面显示的是 Code 而不是 Label：
- 显示 `experience_1` 而不是 "门诊就诊流程更加优化"
- 显示 `quality_1` 而不是 "降低住院患者围手术期死亡率"

## 🔍 问题原因

前端直接使用了 Code 字段，而没有使用 Label 字段。

## 📋 后端返回的数据（正确的）

```json
{
  "activityInfo": {
    "experienceImproveCode": "outpatient_process",
    "experienceImproveLabel": "门诊就诊流程更加优化",
    "qualityTopicCode": "surgery_mortality",
    "qualityTopicLabel": "降低住院患者围手术期死亡率"
  }
}
```

后端已经正确返回了所有4个Label字段！

## ❌ 前端错误代码

### 错误示例1: 直接使用Code字段

```vue
<template>
  <!-- ❌ 错误：直接显示Code -->
  <div>改善就医环境: {{ activityInfo.experienceImproveCode }}</div>
  <div>医疗质量相关主题: {{ activityInfo.qualityTopicCode }}</div>
</template>
```

**显示结果**:
- 改善就医环境: `outpatient_process` ❌
- 医疗质量相关主题: `surgery_mortality` ❌

### 错误示例2: 没有检查Label字段

```javascript
// ❌ 错误：只检查了Code，没有使用Label
if (activityInfo.experienceImproveCode) {
  display = activityInfo.experienceImproveCode  // 显示Code
}
```

### 错误示例3: 字段名写错

```vue
<template>
  <!-- ❌ 错误：字段名写错了 -->
  <div>{{ activityInfo.experienceLabel }}</div>  <!-- 应该是 experienceImproveLabel -->
  <div>{{ activityInfo.qualityLabel }}</div>     <!-- 应该是 qualityTopicLabel -->
</template>
```

## ✅ 正确的前端代码

### 正确示例1: 优先使用Label

```vue
<template>
  <!-- ✅ 正确：优先使用Label，Label为空时才显示Code -->
  <div>改善就医环境: {{ activityInfo.experienceImproveLabel || activityInfo.experienceImproveCode }}</div>
  <div>医疗质量相关主题: {{ activityInfo.qualityTopicLabel || activityInfo.qualityTopicCode }}</div>
</template>
```

**显示结果**:
- 改善就医环境: `门诊就诊流程更加优化` ✅
- 医疗质量相关主题: `降低住院患者围手术期死亡率` ✅

### 正确示例2: 使用计算属性

```vue
<template>
  <div>改善就医环境: {{ experienceImproveDisplay }}</div>
  <div>医疗质量相关主题: {{ qualityTopicDisplay }}</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps(['activityInfo'])

const experienceImproveDisplay = computed(() => {
  if (!props.activityInfo.experienceImproveCode) {
    return '未填写'
  }
  
  // 如果是"其他"，显示Other字段
  if (props.activityInfo.experienceImproveCode === 'other') {
    return props.activityInfo.experienceImproveOther || '其他'
  }
  
  // 优先显示Label，Label为空时显示Code
  return props.activityInfo.experienceImproveLabel || props.activityInfo.experienceImproveCode
})

const qualityTopicDisplay = computed(() => {
  if (!props.activityInfo.qualityTopicCode) {
    return '未填写'
  }
  
  // 如果是"其他"，显示Other字段
  if (props.activityInfo.qualityTopicCode === 'other') {
    return props.activityInfo.qualityTopicOther || '其他'
  }
  
  // 优先显示Label，Label为空时显示Code
  return props.activityInfo.qualityTopicLabel || props.activityInfo.qualityTopicCode
})
</script>
```

### 正确示例3: 使用方法

```vue
<template>
  <div>改善就医环境: {{ getExperienceImproveDisplay() }}</div>
  <div>医疗质量相关主题: {{ getQualityTopicDisplay() }}</div>
</template>

<script setup>
const props = defineProps(['activityInfo'])

const getExperienceImproveDisplay = () => {
  const info = props.activityInfo
  
  if (!info.experienceImproveCode) {
    return '未填写'
  }
  
  if (info.experienceImproveCode === 'other') {
    return info.experienceImproveOther || '其他'
  }
  
  return info.experienceImproveLabel || info.experienceImproveCode
}

const getQualityTopicDisplay = () => {
  const info = props.activityInfo
  
  if (!info.qualityTopicCode) {
    return '未填写'
  }
  
  if (info.qualityTopicCode === 'other') {
    return info.qualityTopicOther || '其他'
  }
  
  return info.qualityTopicLabel || info.qualityTopicCode
}
</script>
```

## 📝 完整的4个字段显示

```vue
<template>
  <el-descriptions :column="2" border>
    <!-- 主题类型 -->
    <el-descriptions-item label="主题类型">
      {{ activityInfo.subjectTypeLabel || activityInfo.subjectTypeCode || '未填写' }}
    </el-descriptions-item>
    
    <!-- 运用手法 -->
    <el-descriptions-item label="运用手法">
      {{ activityInfo.methodLabel || activityInfo.methodCode || '未填写' }}
    </el-descriptions-item>
    
    <!-- 改善就医环境 -->
    <el-descriptions-item label="改善就医环境">
      {{ getExperienceImproveDisplay() }}
    </el-descriptions-item>
    
    <!-- 医疗质量相关主题 -->
    <el-descriptions-item label="医疗质量相关主题">
      {{ getQualityTopicDisplay() }}
    </el-descriptions-item>
  </el-descriptions>
</template>

<script setup>
const props = defineProps(['activityInfo'])

const getExperienceImproveDisplay = () => {
  const info = props.activityInfo
  if (!info.experienceImproveCode) return '未填写'
  if (info.experienceImproveCode === 'other') return info.experienceImproveOther || '其他'
  return info.experienceImproveLabel || info.experienceImproveCode
}

const getQualityTopicDisplay = () => {
  const info = props.activityInfo
  if (!info.qualityTopicCode) return '未填写'
  if (info.qualityTopicCode === 'other') return info.qualityTopicOther || '其他'
  return info.qualityTopicLabel || info.qualityTopicCode
}
</script>
```

## 🔍 排查步骤

如果前端显示的是Code而不是Label，按以下步骤排查：

### 1. 检查API返回数据

在浏览器开发者工具的Network标签中，查看API响应：

```json
// 检查 activityInfo 对象是否包含Label字段
{
  "experienceImproveCode": "outpatient_process",
  "experienceImproveLabel": "门诊就诊流程更加优化",  // ← 这个字段存在吗？
  "qualityTopicCode": "surgery_mortality",
  "qualityTopicLabel": "降低住院患者围手术期死亡率"  // ← 这个字段存在吗？
}
```

如果Label字段不存在，说明后端有问题。
如果Label字段存在，说明前端代码有问题。

### 2. 检查前端代码

搜索前端代码中使用这些字段的地方：

```bash
# 搜索 experienceImproveCode
grep -r "experienceImproveCode" src/

# 搜索 qualityTopicCode
grep -r "qualityTopicCode" src/
```

检查是否直接使用了Code字段，而没有使用Label字段。

### 3. 检查字段名是否正确

常见的字段名错误：
- ❌ `experienceLabel` → ✅ `experienceImproveLabel`
- ❌ `qualityLabel` → ✅ `qualityTopicLabel`
- ❌ `experience_improve_label` → ✅ `experienceImproveLabel` (驼峰命名)

### 4. 检查是否有缓存

清除浏览器缓存，刷新页面，确保使用的是最新的代码。

## 📋 检查清单

- [ ] API返回数据中包含4个Label字段
- [ ] 前端代码优先使用Label字段
- [ ] 字段名拼写正确（驼峰命名）
- [ ] 处理了"其他"选项的特殊情况
- [ ] 处理了空值情况
- [ ] 清除了浏览器缓存

## 🎯 快速修复

如果你的前端代码是这样的：

```vue
<!-- ❌ 错误 -->
<div>{{ activityInfo.experienceImproveCode }}</div>
<div>{{ activityInfo.qualityTopicCode }}</div>
```

快速修复为：

```vue
<!-- ✅ 正确 -->
<div>{{ activityInfo.experienceImproveLabel || activityInfo.experienceImproveCode || '未填写' }}</div>
<div>{{ activityInfo.qualityTopicLabel || activityInfo.qualityTopicCode || '未填写' }}</div>
```

## 📚 相关文档

- `前端开发指引-分场景API调用.md` - 完整的API调用指引
- `Label字段快速参考.txt` - 快速参考
- `Label字段添加完成报告.md` - 技术报告

---

**更新时间**: 2026-02-09  
**问题**: 前端显示Code而不是Label  
**原因**: 前端代码直接使用了Code字段  
**解决**: 优先使用Label字段，Label为空时才显示Code
