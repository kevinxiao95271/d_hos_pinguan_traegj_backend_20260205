#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出机构列表供核对"""

import pymysql
from db_config import DB_CONFIG
import csv

# DB_CONFIG imported from db_config.py

def export_institutions():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                id,
                name,
                region,
                level,
                code,
                uscc
            FROM institutions
            ORDER BY id
        """)
        
        institutions = cursor.fetchall()
        
        # 输出到控制台
        print("=" * 100)
        print("机构列表（供核对地区信息）")
        print("=" * 100)
        print(f"{'ID':<5} {'机构名称':<50} {'当前地区':<10} {'等级':<15}")
        print("-" * 100)
        
        for inst in institutions:
            inst_id = inst[0]
            name = inst[1]
            region = inst[2] if inst[2] else '【空】'
            level = inst[3] if inst[3] else '【空】'
            
            print(f"{inst_id:<5} {name:<50} {region:<10} {level:<15}")
        
        print("-" * 100)
        print(f"总计: {len(institutions)} 个机构")
        print()
        
        # 导出到CSV文件
        csv_filename = 'institutions_list.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', '机构名称', '当前地区', '建议地区', '等级', '代码', '统一社会信用代码'])
            
            for inst in institutions:
                inst_id = inst[0]
                name = inst[1]
                region = inst[2] if inst[2] else ''
                level = inst[3] if inst[3] else ''
                code = inst[4] if inst[4] else ''
                uscc = inst[5] if inst[5] else ''
                
                # 根据名称推测建议地区
                suggested_region = ''
                if '浙江' in name or '省' in name:
                    if '宁波' not in name and '温州' not in name and '绍兴' not in name:
                        suggested_region = '杭州'
                elif '杭州' in name:
                    suggested_region = '杭州'
                elif '宁波' in name:
                    suggested_region = '宁波'
                elif '温州' in name:
                    suggested_region = '温州'
                elif '绍兴' in name:
                    suggested_region = '绍兴'
                elif '嘉兴' in name:
                    suggested_region = '嘉兴'
                elif '湖州' in name:
                    suggested_region = '湖州'
                elif '金华' in name:
                    suggested_region = '金华'
                elif '衢州' in name:
                    suggested_region = '衢州'
                elif '舟山' in name:
                    suggested_region = '舟山'
                elif '台州' in name:
                    suggested_region = '台州'
                elif '丽水' in name:
                    suggested_region = '丽水'
                
                writer.writerow([inst_id, name, region, suggested_region, level, code, uscc])
        
        print(f"✅ 已导出到文件: {csv_filename}")
        print(f"   请在Excel中打开该文件，核对当前地区和建议地区列")
        print()
        
        # 列出明显错误的案例
        print("=" * 100)
        print("明显错误的案例（当前地区与机构名称不符）")
        print("=" * 100)
        
        errors = []
        for inst in institutions:
            inst_id = inst[0]
            name = inst[1]
            region = inst[2] if inst[2] else ''
            
            # 检查明显错误
            if '杭州' in name and region != '杭州':
                errors.append((inst_id, name, region, '杭州'))
            elif '宁波' in name and region != '宁波':
                errors.append((inst_id, name, region, '宁波'))
            elif '温州' in name and region != '温州':
                errors.append((inst_id, name, region, '温州'))
            elif '绍兴' in name and region != '绍兴':
                errors.append((inst_id, name, region, '绍兴'))
            elif '嘉兴' in name and region != '嘉兴':
                errors.append((inst_id, name, region, '嘉兴'))
            elif '湖州' in name and region != '湖州':
                errors.append((inst_id, name, region, '湖州'))
            elif '金华' in name and region != '金华':
                errors.append((inst_id, name, region, '金华'))
            elif '衢州' in name and region != '衢州':
                errors.append((inst_id, name, region, '衢州'))
            elif '舟山' in name and region != '舟山':
                errors.append((inst_id, name, region, '舟山'))
            elif '台州' in name and region != '台州':
                errors.append((inst_id, name, region, '台州'))
            elif '丽水' in name and region != '丽水':
                errors.append((inst_id, name, region, '丽水'))
            elif ('浙江' in name or name.startswith('省')) and region != '杭州':
                if '宁波' not in name and '温州' not in name:
                    errors.append((inst_id, name, region, '杭州（省级医院）'))
        
        if errors:
            print(f"发现 {len(errors)} 个明显错误：\n")
            for error in errors:
                print(f"  ID {error[0]}: {error[1]}")
                print(f"    当前地区: {error[2]}")
                print(f"    应该是: {error[3]}")
                print()
        else:
            print("未发现明显错误")
                    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    export_institutions()
