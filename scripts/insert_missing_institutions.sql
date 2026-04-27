-- 从 const_init_institutions 补充缺失的 23 个机构
INSERT IGNORE INTO `institutions`
    (`name`, `code`, `uscc`, `region`, `city`, `level`, `is_ext`, `created_at`)
SELECT `name`, `code`, `uscc`, `region`, `city`, `level`, 0, NOW()
FROM `const_init_institutions`
WHERE `code` IN (
  'INST_3D3022BB',  -- 丽水市中心医院
  'INST_93721894',  -- 嘉兴市第一医院
  'INST_4EB0EDDC',  -- 嘉兴市第二医院
  'INST_FC52691E',  -- 宁波市第二医院
  'INST_ADAD0AE2',  -- 杭州市中医院
  'INST_9FDB0114',  -- 杭州市第一人民医院
  'INST_FF6A4CA4',  -- 浙江大学医学院附属儿童医院
  'INST_6F60459B',  -- 浙江大学医学院附属妇产科医院
  'INST_032791FA',  -- 浙江大学医学院附属第一医院
  'INST_DD96F580',  -- 浙江大学医学院附属第二医院
  'INST_C4965CF6',  -- 浙江大学医学院附属邵逸夫医院
  'INST_A41D04A9',  -- 浙江省中医院
  'INST_3BF4E206',  -- 浙江省人民医院
  'INST_7612BA7A',  -- 浙江省肿瘤医院
  'INST_07CD220F',  -- 温州医科大学附属眼视光医院
  'INST_862F1CC5',  -- 温州医科大学附属第一医院
  'INST_B0DDC330',  -- 温州医科大学附属第二医院
  'INST_FDB1C565',  -- 湖州市中心医院
  'INST_F9F9721D',  -- 绍兴市人民医院
  'INST_5AA54E58',  -- 衢州市人民医院
  'INST_C019D185',  -- 金华市中心医院
  'INST_25F6D544',  -- 宁波大学附属第一医院（专家文件写作"宁波市第一医院"）
  'INST_7C1ECEEB'   -- 湖州师范学院附属第一医院（专家文件写作"湖州市第一人民医院"）
);