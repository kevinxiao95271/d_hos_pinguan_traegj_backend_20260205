#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""插入字典数据"""

import pymysql
from db_config import DB_CONFIG

# DB_CONFIG imported from db_config.py

def insert_dictionary_data():
    """插入字典数据"""
    print("=" * 80)
    print("插入字典数据")
    print("=" * 80)
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("\n✅ 数据库连接成功")
        
        # 改善就医环境选项
        print("\n1. 插入改善就医环境选项...")
        experience_improve_data = [
            ('experience_improve', 'appointment_service', '预约诊疗服务更加便捷'),
            ('experience_improve', 'outpatient_process', '门诊就诊更加优化'),
            ('experience_improve', 'inpatient_experience', '患者住院体验更加舒适'),
            ('experience_improve', 'post_hospital_service', '院后医疗服务更加连续'),
            ('experience_improve', 'pre_inpatient_connection', '院前院内衔接更加高效'),
            ('experience_improve', 'comfortable_environment', '舒心就医环境更加温馨'),
            ('experience_improve', 'internet_diagnosis', '互联网诊疗更加便捷'),
            ('experience_improve', 'other', '其他')
        ]
        
        for type_val, code, label in experience_improve_data:
            cursor.execute("SELECT id FROM dictionary_items WHERE type = %s AND code = %s", (type_val, code))
            if cursor.fetchone():
                print(f"  ⚠️  {label} 已存在")
            else:
                cursor.execute("""
                    INSERT INTO dictionary_items (type, code, label, active, created_at)
                    VALUES (%s, %s, %s, TRUE, NOW())
                """, (type_val, code, label))
                print(f"  ✅ {label}")
        
        conn.commit()
        
        # 医疗质量安全相关主题选项
        print("\n2. 插入医疗质量安全相关主题选项...")
        quality_topic_data = [
            ('quality_topic', 'stemi_reperfusion', '提高急性ST段抬高型心肌梗死再灌注治疗率'),
            ('quality_topic', 'stroke_reperfusion', '提高急性脑梗死再灌注治疗率'),
            ('quality_topic', 'tumor_tnm_staging', '提高肿瘤治疗前临床TNM分期评估率'),
            ('quality_topic', 'antibiotic_pathogen_test', '提高住院患者抗菌药物治疗前病原学送检率'),
            ('quality_topic', 'perioperative_mortality', '降低住院患者围手术期死亡率'),
            ('quality_topic', 'vte_prevention', '提高静脉血栓栓塞症规范预防率'),
            ('quality_topic', 'septic_shock_bundle', '提高感染性休克集束化治疗完成率'),
            ('quality_topic', 'adverse_event_report', '提高医疗质量安全不良事件报告率'),
            ('quality_topic', 'iv_infusion_standard', '降低住院患者静脉输液规范使用率'),
            ('quality_topic', 'level4_surgery_mdt', '提高四级手术术前多学科讨论完成率'),
            ('quality_topic', 'vaginal_delivery_complication', '降低阴道分娩并发症发生率'),
            ('quality_topic', 'unplanned_reoperation', '降低非计划重返手术室再手术率'),
            ('quality_topic', 'key_diagnosis_record', '提高关键诊疗行为相关记录完整率'),
            ('quality_topic', 'other', '其他')
        ]
        
        for type_val, code, label in quality_topic_data:
            cursor.execute("SELECT id FROM dictionary_items WHERE type = %s AND code = %s", (type_val, code))
            if cursor.fetchone():
                print(f"  ⚠️  {label} 已存在")
            else:
                cursor.execute("""
                    INSERT INTO dictionary_items (type, code, label, active, created_at)
                    VALUES (%s, %s, %s, TRUE, NOW())
                """, (type_val, code, label))
                print(f"  ✅ {label}")
        
        conn.commit()
        
        # 验证
        print("\n3. 验证插入结果...")
        cursor.execute("""
            SELECT type, COUNT(*) as count 
            FROM dictionary_items 
            WHERE type IN ('experience_improve', 'quality_topic')
            GROUP BY type
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} 条")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ 字典数据插入完成！")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ 插入失败: {e}")
        return False

if __name__ == "__main__":
    insert_dictionary_data()
