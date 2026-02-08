# 通知后端 - quality_topic 乱码问题

## 🚨 紧急问题

发现 `quality_topic_7` 等11个code的Label值为乱码（问号），导致前端显示异常。

## 📋 问题详情

### 乱码的code列表

以下11个code的Label值为乱码：

1. `quality_topic_1` - Label: ???????????????
2. `quality_topic_2` - Label: ?????????TNM?????
3. `quality_topic_3` - Label: ??????????????
4. `quality_topic_4` - Label: ???????????????
5. `quality_topic_5` - Label: ???????????????
6. `quality_topic_6` - Label: ????????????????
7. `quality_topic_7` - Label: ??????????????? ← 前端反馈的这个
8. `quality_topic_8` - Label: ??????????????
9. `quality_topic_9` - Label: ???????????????
10. `quality_topic_10` - Label: ???????????????
11. `quality_topic_11` - Label: ??

### 影响范围

**有30条报名记录使用了这些乱码code**：

| Code | 使用次数 | 示例项目 |
|------|---------|---------|
| quality_topic_1 | 5条 | 护理交接班规范化-25 |
| quality_topic_2 | 4条 | 医技检查协调优化-5 |
| quality_topic_3 | 3条 | 手术室周转优化-20 |
| quality_topic_4 | 1条 | 住院服务效率提升-9 |
| quality_topic_5 | 9条 | 疼痛管理规范化-4 |
| quality_topic_6 | 1条 | 疼痛管理规范化-28 |
| quality_topic_7 | 2条 | 护理交接班规范化-1 |
| quality_topic_8 | 1条 | 病案质量提升-12 |
| quality_topic_9 | 3条 | 医疗耗材精细化管理-6 |
| quality_topic_11 | 1条 | 手卫生依从性提升-17 |

## ✅ 已完成的修复

### 1. 删除乱码字典记录

已从 `dictionary_items` 表中删除所有11条乱码记录。

运行脚本：`python fix_quality_topic_labels.py`

结果：
- ✅ 删除了11条乱码记录
- ✅ 保留了27条正确的中文记录

### 2. 验证正确的字典数据

现在 `dictionary_items` 表中只有正确的中文Label：

- stemi_reperfusion → 提高急性ST段抬高型心肌梗死再灌注治疗率
- stroke_reperfusion → 提高急性脑梗死再灌注治疗率
- tumor_tnm_staging → 提高肿瘤治疗前临床TNM分期评估率
- antibiotic_pathogen_test → 提高住院患者抗菌药物治疗前病原学送检率
- perioperative_mortality → 降低住院患者围手术期死亡率
- vte_prevention → 提高静脉血栓栓塞症规范预防率
- septic_shock_bundle → 提高感染性休克集束化治疗完成率
- adverse_event_report → 提高医疗质量安全不良事件报告率
- iv_infusion_standard → 降低住院患者静脉输液规范使用率
- level4_surgery_mdt → 提高四级手术术前多学科讨论完成率
- vaginal_delivery_complication → 降低阴道分娩并发症发生率
- unplanned_reoperation → 降低非计划重返手术室再手术率
- key_diagnosis_record → 提高关键诊疗行为相关记录完整率
- other → 其他

## ⚠️  需要后端处理的问题

### 更新报名记录中的code

**有30条报名记录的 `quality_topic_code` 需要更新为正确的值。**

#### 方案1: 根据项目名称推断正确的code（推荐）

需要后端开发人员根据项目名称和实际情况，手动更新每条记录的code。

例如：
- "提高全院感染性休克集束化治疗完成率" → `septic_shock_bundle`
- "提高严重创伤患者送急诊手术60min达标率" → 可能是 `perioperative_mortality`
- "提高住院患者静脉输液规范使用率" → `iv_infusion_standard`

#### 方案2: 设置为 "other"（临时方案）

如果无法确定正确的code，可以临时设置为 `other`：

```sql
UPDATE activity_infos
SET quality_topic_code = 'other'
WHERE quality_topic_code IN (
  'quality_topic_1', 'quality_topic_2', 'quality_topic_3',
  'quality_topic_4', 'quality_topic_5', 'quality_topic_6',
  'quality_topic_7', 'quality_topic_8', 'quality_topic_9',
  'quality_topic_10', 'quality_topic_11'
);
```

#### 方案3: 设置为NULL（不推荐）

```sql
UPDATE activity_infos
SET quality_topic_code = NULL
WHERE quality_topic_code IN (
  'quality_topic_1', 'quality_topic_2', 'quality_topic_3',
  'quality_topic_4', 'quality_topic_5', 'quality_topic_6',
  'quality_topic_7', 'quality_topic_8', 'quality_topic_9',
  'quality_topic_10', 'quality_topic_11'
);
```

## 📊 详细的受影响记录

### quality_topic_7 (2条记录)

1. ActivityInfo ID: 100, Registration ID: 106, Project: 护理交接班规范化-1
2. ActivityInfo ID: 122, Registration ID: 128, Project: 药学服务质量提升-23

### quality_topic_5 (9条记录)

1. ActivityInfo ID: 103, Registration ID: 109, Project: 疼痛管理规范化-4
2. ActivityInfo ID: 117, Registration ID: 123, Project: 急诊分诊优化-18
3. ActivityInfo ID: 129, Registration ID: 135, Project: 医疗耗材精细化管理-30
4. ActivityInfo ID: 141, Registration ID: 151, Project: 基于信息交互的适老化院内转运实践系统的构建与应用
5. ActivityInfo ID: 145, Registration ID: 155, Project: 基于多学科的全病程呼吸治疗管理体系的构建与应用
6. （还有4条...）

### quality_topic_1 (5条记录)

1. ActivityInfo ID: 124, Registration ID: 130, Project: 护理交接班规范化-25
2. ActivityInfo ID: 142, Registration ID: 152, Project: 提高严重创伤患者送急诊手术60min达标率
3. ActivityInfo ID: 144, Registration ID: 154, Project: 提高全院感染性休克集束化治疗完成率
4. ActivityInfo ID: 156, Registration ID: 159, Project: 提高严重创伤患者送急诊手术60min达标率
5. ActivityInfo ID: 158, Registration ID: 161, Project: 提高全院感染性休克集束化治疗完成率

（其他记录详见 `check_bad_quality_topic_usage.py` 输出）

## 🔧 检查脚本

已创建以下脚本供后端使用：

1. **check_quality_topic_7.py** - 检查乱码记录
2. **fix_quality_topic_labels.py** - 删除乱码字典记录（已执行）
3. **check_bad_quality_topic_usage.py** - 检查使用乱码code的报名记录

运行方式：
```bash
python check_bad_quality_topic_usage.py
```

## 📝 建议的处理步骤

### 步骤1: 导出受影响的记录

```sql
SELECT 
    ai.id as activity_info_id,
    r.id as registration_id,
    r.project_name,
    ai.quality_topic_code,
    ai.quality_topic_other
FROM activity_infos ai
JOIN registrations r ON ai.registration_id = r.id
WHERE ai.quality_topic_code IN (
  'quality_topic_1', 'quality_topic_2', 'quality_topic_3',
  'quality_topic_4', 'quality_topic_5', 'quality_topic_6',
  'quality_topic_7', 'quality_topic_8', 'quality_topic_9',
  'quality_topic_10', 'quality_topic_11'
)
ORDER BY ai.quality_topic_code, r.id;
```

### 步骤2: 根据项目名称确定正确的code

查看每个项目的名称，确定应该使用哪个正确的code。

可用的正确code：
- stemi_reperfusion
- stroke_reperfusion
- tumor_tnm_staging
- antibiotic_pathogen_test
- perioperative_mortality
- vte_prevention
- septic_shock_bundle
- adverse_event_report
- iv_infusion_standard
- level4_surgery_mdt
- vaginal_delivery_complication
- unplanned_reoperation
- key_diagnosis_record
- other

### 步骤3: 批量更新

根据确定的映射关系，批量更新：

```sql
-- 示例：将 quality_topic_1 更新为 septic_shock_bundle
UPDATE activity_infos
SET quality_topic_code = 'septic_shock_bundle'
WHERE id IN (144, 158);  -- 根据实际情况填写ID

-- 或者临时设置为 other
UPDATE activity_infos
SET quality_topic_code = 'other'
WHERE quality_topic_code IN (
  'quality_topic_1', 'quality_topic_2', 'quality_topic_3',
  'quality_topic_4', 'quality_topic_5', 'quality_topic_6',
  'quality_topic_7', 'quality_topic_8', 'quality_topic_9',
  'quality_topic_10', 'quality_topic_11'
);
```

### 步骤4: 验证更新结果

```sql
-- 检查是否还有使用乱码code的记录
SELECT quality_topic_code, COUNT(*) as count
FROM activity_infos
WHERE quality_topic_code IN (
  'quality_topic_1', 'quality_topic_2', 'quality_topic_3',
  'quality_topic_4', 'quality_topic_5', 'quality_topic_6',
  'quality_topic_7', 'quality_topic_8', 'quality_topic_9',
  'quality_topic_10', 'quality_topic_11'
)
GROUP BY quality_topic_code;

-- 应该返回0条记录
```

## 🎯 预期结果

更新完成后：
- ✅ 所有报名记录的 `quality_topic_code` 都使用正确的code
- ✅ API返回的 `qualityTopicLabel` 都是正确的中文
- ✅ 前端显示正常，不再有问号

## 📚 相关文档

- `quality_topic乱码修复报告.md` - 详细的修复报告
- `check_quality_topic_7.py` - 检查脚本
- `fix_quality_topic_labels.py` - 修复脚本
- `check_bad_quality_topic_usage.py` - 使用情况检查脚本

---

**报告时间**: 2026-02-09  
**问题**: quality_topic_7 等11个code的Label为乱码  
**影响**: 30条报名记录  
**已完成**: 删除乱码字典记录  
**待处理**: 更新报名记录中的code  
**优先级**: 🔴 高
