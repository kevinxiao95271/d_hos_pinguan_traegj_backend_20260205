# PostgreSQL新库迁移说明

## ✅ 迁移已完成

### 1. 创建新数据库
- 数据库名: `d_hos_pinguan_20260211`
- 编码: UTF8
- 状态: ✅ 已创建

### 2. 旧库表重命名
已将zjylzl schema中的项目表重命名为 `*_discard`:
- competitions → competitions_discard
- institutions → institutions_discard
- user_accounts → user_accounts_discard
- registrations → registrations_discard
- registration_members → registration_members_discard
- activity_infos → activity_infos_discard
- project_summaries → project_summaries_discard
- material_files → material_files_discard
- review_tasks → review_tasks_discard
- review_scores → review_scores_discard
- dictionary_items → dictionary_items_discard
- system_settings → system_settings_discard
- institution_update_requests → institution_update_requests_discard
- activity_templates → activity_templates_discard
- competition_templates → competition_templates_discard
- pinguan_his_data → pinguan_his_data_discard

### 3. 表结构创建
- ✅ 新库中已创建16个表（由Hibernate自动创建）
- ✅ 表结构基于Entity类定义
- ⚠️ 旧库中的部分字段未迁移（Entity类中未定义）：
  - competitions表: description, status, start_date, end_date, updated_at
  - institutions表: province, city, district, status, updated_at

### 4. 数据迁移
✅ 所有数据已成功迁移到新库:

| 表名 | 新库行数 | 旧库行数 | 状态 |
|------|---------|---------|------|
| dictionary_items | 110 | 110 | ✅ |
| system_settings | 2 | 2 | ✅ |
| competitions | 3 | 3 | ✅ |
| institutions | 40 | 40 | ✅ |
| user_accounts | 74 | 74 | ✅ |
| activity_templates | 0 | 0 | ✅ |
| competition_templates | 1 | 1 | ✅ |
| activity_infos | 45 | 45 | ✅ |
| registrations | 47 | 47 | ✅ |
| registration_members | 189 | 189 | ✅ |
| project_summaries | 46 | 46 | ✅ |
| material_files | 0 | 0 | ✅ |
| review_tasks | 7 | 7 | ✅ |
| review_scores | 3 | 3 | ✅ |
| institution_update_requests | 10 | 10 | ✅ |
| pinguan_his_data | 1818 | 1818 | ✅ |

**总计**: 2395行数据成功迁移

## 配置文件

### application.yml
```yaml
app:
  datasource:
    active: ds1
    ds1:
      url: jdbc:postgresql://119.167.165.27:5432/d_hos_pinguan_20260211
      username: postgres
      password: zjylzl
      driver-class-name: org.postgresql.Driver
```

### 数据库连接信息
- Host: 119.167.165.27
- Port: 5432
- Database: d_hos_pinguan_20260211
- Username: postgres
- Password: zjylzl
- Schema: public (默认)

## 下一步操作

### 启动应用测试
```bash
mvn spring-boot:run
```

应用会连接到新库`d_hos_pinguan_20260211`，所有功能应该正常工作。

## 回滚方案

如果需要回滚到旧库:
1. 修改 `application.yml` 中的数据库名为 `zjylzl`
2. 在zjylzl schema中将 `*_discard` 表改回原名
3. 重启应用

## 迁移脚本

已创建的迁移脚本:
- `scripts/list_all_pg_databases.py` - 列出所有数据库
- `scripts/check_new_db_status.py` - 检查新库状态
- `scripts/migrate_data_to_new_db.py` - 数据迁移主脚本
- `scripts/compare_table_structures.py` - 比较表结构差异
- `scripts/fix_activity_infos_migration.py` - 修复activity_infos迁移
