# 验证Excel文件并修复等级数据

## 步骤1：复制Excel文件

请在命令行中执行以下命令，将Excel文件复制到项目根目录：

```powershell
copy "D:\iWork\iYuo\浙江\品管大赛\工作群文件\2026.1全省医疗机构目录（按地市）（电子化注册系统导出）(1).xlsx" "D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\"
```

或者手动复制文件到：
```
D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\
```

## 步骤2：运行验证脚本

```bash
cd D:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205
python scripts/verify_and_fix_levels.py
```

## 脚本会做什么？

1. ✅ 读取Excel文件
2. ✅ 分析Excel中的等级分布
3. ✅ 对比数据库和字典表
4. ✅ 显示需要删除的等级（如：二甲、三甲）
5. ✅ 显示需要添加的等级（如果Excel中有新的）
6. ⏸️ 询问是否执行修复
7. ✅ 删除多余的等级（二甲、三甲等）
8. ✅ 添加缺失的等级
9. ✅ 验证修复结果

## 预期结果

**修复前字典表：**
- 一级、一甲、一乙
- 二级、二甲、二乙
- 三级、三甲、三乙、三丙
- 未分级
（共11种）

**修复后字典表：**
- 一级
- 二级
- 三级
- 未分级（如果Excel中有）
（只保留Excel中实际存在的等级）

## 如果找不到文件

脚本会提示您将文件重命名为：`医疗机构目录.xlsx`

然后放到项目根目录。
