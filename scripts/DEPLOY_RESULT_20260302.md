# 生产初始化结果包（2026-03-02）

## 一、已准备文件

1. `fix_const_init_constraints_name_uscc_unique.sql`  
   - `const_init_institutions` 约束修正：`name + uscc` 唯一，`uscc` 非唯一
2. `fix_institutions_constraints_name_uscc_unique.sql`  
   - `institutions` 约束修正：`name + uscc` 唯一，`uscc` 非唯一
3. `init_prod_const_init_institutions_no_created_at.csv`  
   - `const_init_institutions` 全量 CSV（42094 行，不含 `created_at`）
4. `init_prod_dictionary_items.sql`  
   - 字典初始化 SQL
5. `init_prod_competitions.sql`  
   - 赛事初始化 SQL
6. `init_prod_system_settings.sql`  
   - 系统设置初始化 SQL（含 `currentCompetitionId=1`）
7. `init_prod_institutions_and_reviewers.sql`  
   - 机构 + 评审专家初始化 SQL（来源：`专家信息一览表_含机构全称.xls`）
8. `init_prod_reviewers_skipped.csv`  
   - 跳过记录清单（缺手机号/机构全称）
9. `init_prod_admin_accounts.sql`  
   - 管理账号初始化 SQL（`OPS` 3个，`COMMITTEE_ADMIN` 3个）

## 二、推荐执行顺序

1. 执行 `fix_const_init_constraints_name_uscc_unique.sql`
2. 执行 `fix_institutions_constraints_name_uscc_unique.sql`
3. 清空并导入 `const_init_institutions`：  
   - `TRUNCATE TABLE const_init_institutions;`  
   - Navicat 导入 `init_prod_const_init_institutions_no_created_at.csv`
4. 执行 `init_prod_dictionary_items.sql`
5. 执行 `init_prod_competitions.sql`
6. 执行 `init_prod_system_settings.sql`
7. 执行 `init_prod_institutions_and_reviewers.sql`
8. 执行 `init_prod_admin_accounts.sql`

## 三、仍需手工初始化（非 SQL）

1. 系统模板文件（MinIO + 表记录）  
   - `registration_form`  
   - `result_report`
2. 若需要历史数据页：导入 `pinguan_his_data`（2024/2025 历史数据 xls）

## 四、最小验收检查

1. `select count(*) from const_init_institutions;` -> 42094
2. `select count(*) from competitions;` -> >= 1
3. `select setting_value from system_settings where setting_key='currentCompetitionId';` -> 1
4. `select count(*) from user_accounts where role='OPS';` -> >= 3
5. `select count(*) from user_accounts where role='COMMITTEE_ADMIN';` -> >= 3
6. `select count(*) from user_accounts where role='REVIEWER';` -> >= 90
