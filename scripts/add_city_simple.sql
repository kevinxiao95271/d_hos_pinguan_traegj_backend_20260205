-- 添加city字段并填充数据

-- 1. 添加字段（如果不存在）
ALTER TABLE institutions ADD COLUMN IF NOT EXISTS city VARCHAR(50) COMMENT '所属城市（市级）' AFTER region;

-- 2. 杭州市
UPDATE institutions SET city = '杭州市' WHERE region IN ('上城区', '下城区', '江干区', '拱墅区', '西湖区', '滨江区', '萧山区', '余杭区', '富阳区', '临安区', '桐庐县', '淳安县', '建德市');

-- 3. 宁波市
UPDATE institutions SET city = '宁波市' WHERE region IN ('海曙区', '江北区', '北仑区', '镇海区', '鄞州区', '奉化区', '象山县', '宁海县', '余姚市', '慈溪市');

-- 4. 温州市
UPDATE institutions SET city = '温州市' WHERE region IN ('鹿城区', '龙湾区', '瓯海区', '洞头区', '永嘉县', '平阳县', '苍南县', '文成县', '泰顺县', '瑞安市', '乐清市');

-- 5. 嘉兴市
UPDATE institutions SET city = '嘉兴市' WHERE region IN ('南湖区', '秀洲区', '嘉善县', '海盐县', '海宁市', '平湖市', '桐乡市');

-- 6. 湖州市
UPDATE institutions SET city = '湖州市' WHERE region IN ('吴兴区', '南浔区', '德清县', '长兴县', '安吉县');

-- 7. 绍兴市
UPDATE institutions SET city = '绍兴市' WHERE region IN ('越城区', '柯桥区', '上虞区', '新昌县', '诸暨市', '嵊州市');

-- 8. 金华市
UPDATE institutions SET city = '金华市' WHERE region IN ('婺城区', '金东区', '武义县', '浦江县', '磐安县', '兰溪市', '义乌市', '东阳市', '永康市');

-- 9. 衢州市
UPDATE institutions SET city = '衢州市' WHERE region IN ('柯城区', '衢江区', '常山县', '开化县', '龙游县', '江山市');

-- 10. 舟山市
UPDATE institutions SET city = '舟山市' WHERE region IN ('定海区', '普陀区', '岱山县', '嵊泗县');

-- 11. 台州市
UPDATE institutions SET city = '台州市' WHERE region IN ('椒江区', '黄岩区', '路桥区', '三门县', '天台县', '仙居县', '温岭市', '临海市', '玉环市');

-- 12. 丽水市
UPDATE institutions SET city = '丽水市' WHERE region IN ('莲都区', '青田县', '缙云县', '遂昌县', '松阳县', '云和县', '庆元县', '景宁畲族自治县', '龙泉市');

-- 13. 对于已经是市级的region，直接复制
UPDATE institutions SET city = region WHERE city IS NULL AND region LIKE '%市';

-- 14. 添加索引
CREATE INDEX IF NOT EXISTS idx_city ON institutions(city);

-- 15. 查询统计
SELECT '总机构数' as 统计项, COUNT(*) as 数量 FROM institutions
UNION ALL
SELECT '有city数据', COUNT(*) FROM institutions WHERE city IS NOT NULL
UNION ALL
SELECT '无city数据', COUNT(*) FROM institutions WHERE city IS NULL;

-- 16. TOP 10城市
SELECT city, COUNT(*) as cnt 
FROM institutions 
WHERE city IS NOT NULL 
GROUP BY city 
ORDER BY cnt DESC 
LIMIT 10;

-- 17. 验证杭州市
SELECT '杭州市' as 城市, region as 区县, COUNT(*) as 机构数
FROM institutions 
WHERE city = '杭州市' 
GROUP BY region 
ORDER BY COUNT(*) DESC;
