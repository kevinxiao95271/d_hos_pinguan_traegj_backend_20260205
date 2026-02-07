# 常用SQL查询语句

**数据库**: pinguan_db  
**创建日期**: 2026-02-07

---

## 一、机构查询

### 1.1 查询未报名参赛的机构

```sql
-- 查询某个赛事中未报名的机构
SELECT 
    i.id,
    i.name AS institution_name,
    i.code AS institution_code,
    i.uscc,
    i.created_at
FROM institutions i
WHERE NOT EXISTS (
    SELECT 1 
    FROM registrations r 
    WHERE r.institution_id = i.id 
      AND r.competition_id = 21  -- 替换为具体赛事ID
)
ORDER BY i.name;
```

**说明**: 
- 修改 `competition_id = 21` 为实际的赛事ID
- 返回所有在指定赛事中没有报名记录的机构

---

### 1.2 查询从未参加过任何赛事的机构

```sql
-- 查询从未报名过任何赛事的机构
SELECT 
    i.id,
    i.name AS institution_name,
    i.code AS institution_code,
    i.uscc,
    i.created_at
FROM institutions i
WHERE NOT EXISTS (
    SELECT 1 
    FROM registrations r 
    WHERE r.institution_id = i.id
)
ORDER BY i.name;
```

---

### 1.3 机构参赛统计（每个机构的参赛次数）

```sql
-- 统计每个机构的参赛情况
SELECT 
    i.id,
    i.name AS institution_name,
    i.code AS institution_code,
    COUNT(DISTINCT r.competition_id) AS competition_count,
    COUNT(r.id) AS project_count,
    MAX(r.submitted_at) AS last_registration_date
FROM institutions i
LEFT JOIN registrations r ON r.institution_id = i.id
GROUP BY i.id, i.name, i.code
ORDER BY competition_count DESC, project_count DESC;
```

---

## 二、报名项目查询

### 2.1 查询所有报名的参赛项目

```sql
-- 查询指定赛事的所有报名项目
SELECT 
    r.id,
    r.project_name,
    r.group_type,
    r.group_code,
    r.status,
    r.submitted_at,
    i.name AS institution_name,
    i.code AS institution_code,
    u.name AS applicant_name,
    u.phone AS applicant_phone,
    c.name AS competition_name
FROM registrations r
INNER JOIN competitions c ON r.competition_id = c.id
INNER JOIN institutions i ON r.institution_id = i.id
LEFT JOIN user_accounts u ON r.applicant_id = u.id
WHERE r.competition_id = 21  -- 替换为具体赛事ID
ORDER BY r.submitted_at DESC;
```

---

### 2.2 查询已提交的报名项目（按组别统计）

```sql
-- 按组别统计已提交的报名项目
SELECT 
    r.group_type,
    r.group_code,
    COUNT(*) AS project_count,
    GROUP_CONCAT(DISTINCT i.name ORDER BY i.name SEPARATOR ', ') AS institutions
FROM registrations r
INNER JOIN institutions i ON r.institution_id = i.id
WHERE r.competition_id = 21  -- 替换为具体赛事ID
  AND r.status = 'SUBMITTED'
GROUP BY r.group_type, r.group_code
ORDER BY r.group_type, r.group_code;
```

---

### 2.3 查询报名项目的完整信息（含活动详情）

```sql
-- 查询报名项目的完整信息
SELECT 
    r.id AS registration_id,
    r.project_name,
    r.group_type,
    r.group_code,
    r.status,
    r.submitted_at,
    i.name AS institution_name,
    u.name AS applicant_name,
    -- 活动信息
    ai.theme AS activity_theme,
    ai.keywords,
    ai.method_code,
    ai.subject_type_code,
    ai.avg_age,
    ai.avg_work_years,
    ai.cross_department
FROM registrations r
INNER JOIN institutions i ON r.institution_id = i.id
LEFT JOIN user_accounts u ON r.applicant_id = u.id
LEFT JOIN activity_infos ai ON ai.registration_id = r.id
WHERE r.competition_id = 21
ORDER BY r.submitted_at DESC;
```

---

## 三、评审阶段查询

### 3.1 查询书审阶段的参赛项目

```sql
-- 查询书审阶段的所有参赛项目及评审状态
SELECT 
    r.id AS registration_id,
    r.project_name,
    r.group_type,
    r.group_code,
    i.name AS institution_name,
    -- 评审任务统计
    COUNT(rt.id) AS total_review_tasks,
    SUM(CASE WHEN rt.status = 'SCORED' THEN 1 ELSE 0 END) AS scored_count,
    SUM(CASE WHEN rt.status = 'PENDING' THEN 1 ELSE 0 END) AS pending_count,
    -- 平均分
    AVG(rs.total) AS avg_score,
    MAX(rs.total) AS max_score,
    MIN(rs.total) AS min_score
FROM registrations r
INNER JOIN institutions i ON r.institution_id = i.id
LEFT JOIN review_tasks rt ON rt.registration_id = r.id AND rt.stage = 'BOOK'
LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE r.competition_id = 21
GROUP BY r.id, r.project_name, r.group_type, r.group_code, i.name
ORDER BY avg_score DESC NULLS LAST;
```

---

### 3.2 查询面谈阶段的参赛项目

```sql
-- 查询面谈阶段的所有参赛项目及评审状态
SELECT 
    r.id AS registration_id,
    r.project_name,
    r.group_type,
    r.group_code,
    i.name AS institution_name,
    -- 评审任务统计
    COUNT(rt.id) AS total_review_tasks,
    SUM(CASE WHEN rt.status = 'SCORED' THEN 1 ELSE 0 END) AS scored_count,
    SUM(CASE WHEN rt.status = 'PENDING' THEN 1 ELSE 0 END) AS pending_count,
    -- 平均分
    AVG(rs.total) AS avg_score,
    MAX(rs.total) AS max_score,
    MIN(rs.total) AS min_score
FROM registrations r
INNER JOIN institutions i ON r.institution_id = i.id
LEFT JOIN review_tasks rt ON rt.registration_id = r.id AND rt.stage = 'INTERVIEW'
LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE r.competition_id = 21
GROUP BY r.id, r.project_name, r.group_type, r.group_code, i.name
ORDER BY avg_score DESC NULLS LAST;
```

---

### 3.3 查询决赛阶段的参赛项目

```sql
-- 查询决赛阶段的所有参赛项目及评审状态
SELECT 
    r.id AS registration_id,
    r.project_name,
    r.group_type,
    r.group_code,
    i.name AS institution_name,
    -- 评审任务统计
    COUNT(rt.id) AS total_review_tasks,
    SUM(CASE WHEN rt.status = 'SCORED' THEN 1 ELSE 0 END) AS scored_count,
    SUM(CASE WHEN rt.status = 'PENDING' THEN 1 ELSE 0 END) AS pending_count,
    -- 平均分
    AVG(rs.total) AS avg_score,
    MAX(rs.total) AS max_score,
    MIN(rs.total) AS min_score
FROM registrations r
INNER JOIN institutions i ON r.institution_id = i.id
LEFT JOIN review_tasks rt ON rt.registration_id = r.id AND rt.stage = 'FINAL'
LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE r.competition_id = 21
GROUP BY r.id, r.project_name, r.group_type, r.group_code, i.name
ORDER BY avg_score DESC NULLS LAST;
```

---

### 3.4 查询所有阶段的参赛项目汇总

```sql
-- 查询项目在所有阶段的评审情况
SELECT 
    r.id AS registration_id,
    r.project_name,
    i.name AS institution_name,
    r.group_type,
    r.group_code,
    -- 书审阶段
    COUNT(CASE WHEN rt.stage = 'BOOK' THEN 1 END) AS book_task_count,
    AVG(CASE WHEN rt.stage = 'BOOK' THEN rs.total END) AS book_avg_score,
    -- 面谈阶段
    COUNT(CASE WHEN rt.stage = 'INTERVIEW' THEN 1 END) AS interview_task_count,
    AVG(CASE WHEN rt.stage = 'INTERVIEW' THEN rs.total END) AS interview_avg_score,
    -- 决赛阶段
    COUNT(CASE WHEN rt.stage = 'FINAL' THEN 1 END) AS final_task_count,
    AVG(CASE WHEN rt.stage = 'FINAL' THEN rs.total END) AS final_avg_score
FROM registrations r
INNER JOIN institutions i ON r.institution_id = i.id
LEFT JOIN review_tasks rt ON rt.registration_id = r.id
LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE r.competition_id = 21
GROUP BY r.id, r.project_name, i.name, r.group_type, r.group_code
ORDER BY r.project_name;
```

---

## 四、评审任务得分查询

### 4.1 查询书审阶段的评审得分（详细）

```sql
-- 查询书审阶段的详细评审得分
SELECT 
    rt.id AS task_id,
    r.id AS registration_id,
    r.project_name,
    i.name AS institution_name,
    r.group_type,
    r.group_code,
    -- 评委信息
    u.id AS reviewer_id,
    u.name AS reviewer_name,
    u.title AS reviewer_title,
    inst_reviewer.name AS reviewer_institution,
    -- 评分详情
    rs.plan,
    rs.problem,
    rs.action,
    rs.success,
    rs.review,
    rs.operation,
    rs.presentation,
    rs.total,
    rs.highlight,
    rs.weakness,
    rs.submitted_at AS scored_at,
    rt.created_at AS task_created_at
FROM review_tasks rt
INNER JOIN registrations r ON rt.registration_id = r.id
INNER JOIN institutions i ON r.institution_id = i.id
INNER JOIN user_accounts u ON rt.reviewer_id = u.id
LEFT JOIN institutions inst_reviewer ON u.institution_id = inst_reviewer.id
LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE r.competition_id = 21
  AND rt.stage = 'BOOK'
  AND rt.status = 'SCORED'
ORDER BY r.project_name, rs.total DESC;
```

---

### 4.2 查询面谈阶段的评审得分（详细）

```sql
-- 查询面谈阶段的详细评审得分
SELECT 
    rt.id AS task_id,
    r.id AS registration_id,
    r.project_name,
    i.name AS institution_name,
    r.group_type,
    r.group_code,
    -- 评委信息
    u.id AS reviewer_id,
    u.name AS reviewer_name,
    u.title AS reviewer_title,
    inst_reviewer.name AS reviewer_institution,
    -- 评分详情
    rs.plan,
    rs.problem,
    rs.action,
    rs.success,
    rs.review,
    rs.operation,
    rs.presentation,
    rs.total,
    rs.highlight,
    rs.weakness,
    rs.submitted_at AS scored_at,
    rt.created_at AS task_created_at
FROM review_tasks rt
INNER JOIN registrations r ON rt.registration_id = r.id
INNER JOIN institutions i ON r.institution_id = i.id
INNER JOIN user_accounts u ON rt.reviewer_id = u.id
LEFT JOIN institutions inst_reviewer ON u.institution_id = inst_reviewer.id
LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE r.competition_id = 21
  AND rt.stage = 'INTERVIEW'
  AND rt.status = 'SCORED'
ORDER BY r.project_name, rs.total DESC;
```

---

### 4.3 查询决赛阶段的评审得分（详细）

```sql
-- 查询决赛阶段的详细评审得分
SELECT 
    rt.id AS task_id,
    r.id AS registration_id,
    r.project_name,
    i.name AS institution_name,
    r.group_type,
    r.group_code,
    -- 评委信息
    u.id AS reviewer_id,
    u.name AS reviewer_name,
    u.title AS reviewer_title,
    inst_reviewer.name AS reviewer_institution,
    -- 评分详情
    rs.plan,
    rs.problem,
    rs.action,
    rs.success,
    rs.review,
    rs.operation,
    rs.presentation,
    rs.total,
    rs.highlight,
    rs.weakness,
    rs.submitted_at AS scored_at,
    rt.created_at AS task_created_at
FROM review_tasks rt
INNER JOIN registrations r ON rt.registration_id = r.id
INNER JOIN institutions i ON r.institution_id = i.id
INNER JOIN user_accounts u ON rt.reviewer_id = u.id
LEFT JOIN institutions inst_reviewer ON u.institution_id = inst_reviewer.id
LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE r.competition_id = 21
  AND rt.stage = 'FINAL'
  AND rt.status = 'SCORED'
ORDER BY r.project_name, rs.total DESC;
```

---

### 4.4 查询某个项目的所有阶段评审得分

```sql
-- 查询某个项目在所有阶段的评审得分
SELECT 
    rt.stage,
    u.name AS reviewer_name,
    u.title AS reviewer_title,
    inst_reviewer.name AS reviewer_institution,
    rs.plan,
    rs.problem,
    rs.action,
    rs.success,
    rs.review,
    rs.operation,
    rs.presentation,
    rs.total,
    rs.highlight,
    rs.weakness,
    rs.submitted_at AS scored_at
FROM review_tasks rt
INNER JOIN user_accounts u ON rt.reviewer_id = u.id
LEFT JOIN institutions inst_reviewer ON u.institution_id = inst_reviewer.id
LEFT JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE rt.registration_id = 106  -- 替换为具体项目ID
  AND rt.status = 'SCORED'
ORDER BY 
    CASE rt.stage 
        WHEN 'BOOK' THEN 1 
        WHEN 'INTERVIEW' THEN 2 
        WHEN 'FINAL' THEN 3 
    END,
    rs.total DESC;
```

---

### 4.5 查询评审排名（某个阶段）

```sql
-- 查询书审阶段的项目排名
SELECT 
    RANK() OVER (ORDER BY AVG(rs.total) DESC) AS ranking,
    r.id AS registration_id,
    r.project_name,
    i.name AS institution_name,
    r.group_type,
    r.group_code,
    COUNT(rs.id) AS reviewer_count,
    AVG(rs.total) AS avg_score,
    MAX(rs.total) AS max_score,
    MIN(rs.total) AS min_score,
    STDDEV(rs.total) AS score_stddev
FROM registrations r
INNER JOIN institutions i ON r.institution_id = i.id
INNER JOIN review_tasks rt ON rt.registration_id = r.id
INNER JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE r.competition_id = 21
  AND rt.stage = 'BOOK'
  AND rt.status = 'SCORED'
GROUP BY r.id, r.project_name, i.name, r.group_type, r.group_code
HAVING COUNT(rs.id) > 0
ORDER BY avg_score DESC;
```

---

### 4.6 查询按组别排名

```sql
-- 按组别查询排名（书审阶段）
SELECT 
    r.group_type,
    r.group_code,
    RANK() OVER (PARTITION BY r.group_type ORDER BY AVG(rs.total) DESC) AS group_ranking,
    r.id AS registration_id,
    r.project_name,
    i.name AS institution_name,
    COUNT(rs.id) AS reviewer_count,
    AVG(rs.total) AS avg_score
FROM registrations r
INNER JOIN institutions i ON r.institution_id = i.id
INNER JOIN review_tasks rt ON rt.registration_id = r.id
INNER JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE r.competition_id = 21
  AND rt.stage = 'BOOK'
  AND rt.status = 'SCORED'
GROUP BY r.group_type, r.group_code, r.id, r.project_name, i.name
HAVING COUNT(rs.id) > 0
ORDER BY r.group_type, avg_score DESC;
```

---

## 五、评委工作量统计

### 5.1 查询评委的评审任务统计

```sql
-- 统计每个评委的评审任务和完成情况
SELECT 
    u.id AS reviewer_id,
    u.name AS reviewer_name,
    u.title AS reviewer_title,
    i.name AS institution_name,
    rt.stage,
    COUNT(rt.id) AS total_tasks,
    SUM(CASE WHEN rt.status = 'SCORED' THEN 1 ELSE 0 END) AS scored_count,
    SUM(CASE WHEN rt.status = 'PENDING' THEN 1 ELSE 0 END) AS pending_count,
    ROUND(SUM(CASE WHEN rt.status = 'SCORED' THEN 1 ELSE 0 END) * 100.0 / COUNT(rt.id), 2) AS completion_rate
FROM user_accounts u
INNER JOIN review_tasks rt ON rt.reviewer_id = u.id
INNER JOIN registrations r ON rt.registration_id = r.id
LEFT JOIN institutions i ON u.institution_id = i.id
WHERE r.competition_id = 21
  AND u.role = 'REVIEWER'
GROUP BY u.id, u.name, u.title, i.name, rt.stage
ORDER BY rt.stage, completion_rate DESC, total_tasks DESC;
```

---

### 5.2 查询评委的平均评分分布

```sql
-- 统计评委的平均评分和评分标准差
SELECT 
    u.id AS reviewer_id,
    u.name AS reviewer_name,
    u.title AS reviewer_title,
    rt.stage,
    COUNT(rs.id) AS scored_count,
    AVG(rs.total) AS avg_score,
    STDDEV(rs.total) AS score_stddev,
    MIN(rs.total) AS min_score,
    MAX(rs.total) AS max_score
FROM user_accounts u
INNER JOIN review_tasks rt ON rt.reviewer_id = u.id
INNER JOIN review_scores rs ON rs.review_task_id = rt.id
INNER JOIN registrations r ON rt.registration_id = r.id
WHERE r.competition_id = 21
  AND u.role = 'REVIEWER'
GROUP BY u.id, u.name, u.title, rt.stage
HAVING COUNT(rs.id) > 0
ORDER BY rt.stage, avg_score DESC;
```

---

## 六、综合查询

### 6.1 赛事整体评审进度

```sql
-- 查询赛事整体评审进度
SELECT 
    c.name AS competition_name,
    rt.stage,
    COUNT(DISTINCT r.id) AS total_projects,
    COUNT(rt.id) AS total_tasks,
    SUM(CASE WHEN rt.status = 'SCORED' THEN 1 ELSE 0 END) AS scored_tasks,
    SUM(CASE WHEN rt.status = 'PENDING' THEN 1 ELSE 0 END) AS pending_tasks,
    ROUND(SUM(CASE WHEN rt.status = 'SCORED' THEN 1 ELSE 0 END) * 100.0 / COUNT(rt.id), 2) AS progress_percentage
FROM competitions c
INNER JOIN registrations r ON r.competition_id = c.id
LEFT JOIN review_tasks rt ON rt.registration_id = r.id
WHERE c.id = 21
GROUP BY c.name, rt.stage
ORDER BY 
    CASE rt.stage 
        WHEN 'BOOK' THEN 1 
        WHEN 'INTERVIEW' THEN 2 
        WHEN 'FINAL' THEN 3 
    END;
```

---

### 6.2 找出未被评审的项目

```sql
-- 查询某个阶段中未被分配评审任务的项目
SELECT 
    r.id AS registration_id,
    r.project_name,
    i.name AS institution_name,
    r.group_type,
    r.group_code,
    r.submitted_at
FROM registrations r
INNER JOIN institutions i ON r.institution_id = i.id
WHERE r.competition_id = 21
  AND r.status = 'SUBMITTED'
  AND NOT EXISTS (
      SELECT 1 
      FROM review_tasks rt 
      WHERE rt.registration_id = r.id 
        AND rt.stage = 'BOOK'  -- 替换为具体阶段
  )
ORDER BY r.submitted_at;
```

---

### 6.3 查询评审异常情况

```sql
-- 查询评审异常：评分差异过大的项目
SELECT 
    r.id AS registration_id,
    r.project_name,
    i.name AS institution_name,
    rt.stage,
    COUNT(rs.id) AS reviewer_count,
    AVG(rs.total) AS avg_score,
    MAX(rs.total) - MIN(rs.total) AS score_difference,
    STDDEV(rs.total) AS score_stddev
FROM registrations r
INNER JOIN institutions i ON r.institution_id = i.id
INNER JOIN review_tasks rt ON rt.registration_id = r.id
INNER JOIN review_scores rs ON rs.review_task_id = rt.id
WHERE r.competition_id = 21
  AND rt.status = 'SCORED'
GROUP BY r.id, r.project_name, i.name, rt.stage
HAVING COUNT(rs.id) >= 2 
   AND (MAX(rs.total) - MIN(rs.total)) > 20  -- 评分差异超过20分
ORDER BY score_difference DESC;
```

---

## 七、使用说明

### 替换参数说明

| 占位符 | 说明 | 示例值 |
|--------|------|--------|
| `competition_id = 21` | 赛事ID | 21, 22, 23 |
| `registration_id = 106` | 项目ID | 106, 107, 108 |
| `rt.stage = 'BOOK'` | 评审阶段 | 'BOOK', 'INTERVIEW', 'FINAL' |

### 阶段枚举值

| 枚举值 | 说明 |
|--------|------|
| `BOOK` | 书审阶段 |
| `INTERVIEW` | 面谈阶段 |
| `FINAL` | 决赛阶段 |

### 状态枚举值

| 枚举值 | 说明 |
|--------|------|
| `PENDING` | 待评审 |
| `SCORED` | 已评分 |
| `SUBMITTED` | 已提交（报名状态） |
| `DRAFT` | 草稿（报名状态） |

---

**创建日期**: 2026-02-07  
**数据库版本**: schema_20260205150932.sql
