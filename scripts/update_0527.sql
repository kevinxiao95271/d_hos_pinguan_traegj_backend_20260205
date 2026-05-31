-- ============================================================
-- 2026-05-27 数据更新脚本
-- 包含：医疗机构名称更改 + 项目名称更改
-- ============================================================

-- ------------------------------------------------------------
-- 一、医疗机构名称更改（共15条）
-- 更新 institutions 表的 name 字段
-- ------------------------------------------------------------

UPDATE institutions SET name = '湖州师范大学附属第一医院（湖州市第一人民医院）'
WHERE name = '湖州师范学院附属第一医院（湖州市第一人民医院）';

UPDATE institutions SET name = '缙云县人民医院'
WHERE name = '缙云县人民医院（缙云县人民医院医共体管理中心）';

UPDATE institutions SET name = '绍兴大学附属医院'
WHERE name = '绍兴文理学院附属医院';

UPDATE institutions SET name = '绍兴市上虞妇幼保健院'
WHERE name = '绍兴市上虞妇幼保健院（绍兴市上虞区妇幼保健计划生育服务中心）';

UPDATE institutions SET name = '湖州市第三人民医院'
WHERE name = '湖州市第三人民医院（湖州市精神病医院）';

UPDATE institutions SET name = '庆元县人民医院'
WHERE name = '庆元县人民医院（医共体）';

UPDATE institutions SET name = '景宁畲族自治县人民医院'
WHERE name = '景宁畲族自治县人民医院（县域医共体）';

UPDATE institutions SET name = '慈溪市第三人民医院医疗健康集团'
WHERE name = '慈溪市第三人民医院医疗健康集团（慈溪市第三人民医院）';

UPDATE institutions SET name = '宁波一院龙山医院医疗健康集团'
WHERE name = '宁波一院龙山医院医疗健康集团（慈溪市龙山医院）';

UPDATE institutions SET name = '台州市路桥区第二人民医院医疗服务共同体'
WHERE name = '台州市路桥区第二人民医院医疗服务共同体（台州市路桥区第二人民医院）';

UPDATE institutions SET name = '瑞安市第五人民医院'
WHERE name = '瑞安市第五人民医院（瑞安市第五人民医院互联网医院）';

UPDATE institutions SET name = '缙云县第二人民医院'
WHERE name = '缙云县第二人民医院（缙云县第二人民医院医共体管理中心）';

UPDATE institutions SET name = '慈溪市中西医结合医疗健康集团'
WHERE name = '慈溪市中西医结合医疗健康集团六院院区（慈溪市中医医院）';

UPDATE institutions SET name = '宁波市第九医院'
WHERE name = '宁波市第九医院（宁波市第一医院江北分院、宁波市江北区人民医院）';

-- 第15条：慈溪市中西医结合医疗健康集团（另一个旧名）
-- 目标名称与第13条相同，若已更新则此句影响行数为0（幂等安全）
UPDATE institutions SET name = '慈溪市中西医结合医疗健康集团'
WHERE name = '慈溪市中西医结合医疗健康集团中医院院区（慈溪市中医医院）';


-- ------------------------------------------------------------
-- 二、项目名称更改（共8条，按项目编号即 registrations.id 更新）
-- ------------------------------------------------------------

-- 20260921 浙江医院 进阶组
UPDATE registrations SET project_name = '基于KTA循证实践模型的多参数心电监护仪临床警报管理--"警\'循\'精准，护佑安全"'
WHERE id = 20260921;

-- 20260528 嘉兴市第二医院 进阶组
UPDATE registrations SET project_name = '基于行动研究的维持性血液透析患者睡眠障碍运动训练管理模式构建与实践'
WHERE id = 20260528;

-- 20260562 浙江省人民医院富阳院区 综合组-问题解决型专场（原名含全角引号，更改为同内容，校验格式一致）
UPDATE registrations SET project_name = '"省营县院"背景下提高约束具使用规范率'
WHERE id = 20260562;

-- 20260544 树兰（杭州）医院 综合组-问题解决型专场（"基ITHBC" → "基于ITHBC"）
UPDATE registrations SET project_name = '基于ITHBC理论降低肝移植受者术后饮酒复发率'
WHERE id = 20260544;

-- 20260947 浙江中医药大学附属第二医院 综合组-问题解决型专场（补左引号）
UPDATE registrations SET project_name = '"肺护防线，克菌除险"-降低ICU患者CRKP检出率'
WHERE id = 20260947;

-- 20260899 丽水市第二人民医院 综合组-课达及QFD专场（内容与原名相同，确认无变化）
-- UPDATE registrations SET project_name = '构建"防筛诊治康"五位一体的酒精使用障碍防治体系'
-- WHERE id = 20260899;
-- ↑ 原名与更改后完全一致，跳过（仅保留注释供核查）

-- 20260252 宁波市鄞州区第三医院 基层组（多学科联合 → 多部门联动）
UPDATE registrations SET project_name = '多部门联动提高术前皮肤准备合格率'
WHERE id = 20260252;

-- 20260482 温州医科大学附属眼视光医院 综合组-问题解决型专场（提高 → 降低）
UPDATE registrations SET project_name = '基于危机管理4R模型降低急性闭角型青光眼患者首诊处置时间'
WHERE id = 20260482;
