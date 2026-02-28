#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理重复的材料文件记录
每个报名ID + 文件类型 只保留最新的一个
"""

import pymysql
from minio import Minio
from datetime import datetime
import sys

# 数据库配置（从application.yml获取）
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# MinIO配置
MINIO_CONFIG = {
    'endpoint': '119.167.165.27:58010',
    'access_key': 'minioadmin',
    'secret_key': 'Ygcx2025',
    'bucket': 'registration-files',
    'secure': False
}

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def get_minio_client():
    """获取MinIO客户端"""
    return Minio(
        MINIO_CONFIG['endpoint'],
        access_key=MINIO_CONFIG['access_key'],
        secret_key=MINIO_CONFIG['secret_key'],
        secure=MINIO_CONFIG['secure']
    )

def analyze_duplicates():
    """分析重复记录"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    print("=" * 80)
    print("正在分析重复的材料文件记录...")
    print("=" * 80)
    print()
    
    # 查询重复情况
    query = """
    SELECT 
        registration_id,
        type,
        COUNT(*) as file_count,
        MIN(uploaded_at) as earliest_upload,
        MAX(uploaded_at) as latest_upload
    FROM material_files
    GROUP BY registration_id, type
    HAVING COUNT(*) > 1
    ORDER BY file_count DESC, registration_id, type
    """
    
    cursor.execute(query)
    duplicates = cursor.fetchall()
    
    if not duplicates:
        print("[OK] No duplicate records found! Database is clean.")
        cursor.close()
        conn.close()
        return None
    
    print(f"[WARNING] Found {len(duplicates)} groups of duplicate records:\n")
    
    total_files_to_delete = 0
    
    for dup in duplicates:
        print(f"报名ID: {dup['registration_id']}, 类型: {dup['type']}")
        print(f"  文件数量: {dup['file_count']}")
        print(f"  最早上传: {dup['earliest_upload']}")
        print(f"  最新上传: {dup['latest_upload']}")
        total_files_to_delete += (dup['file_count'] - 1)
        print()
    
    print(f"总计需要删除 {total_files_to_delete} 个旧文件")
    print()
    
    cursor.close()
    conn.close()
    
    return duplicates

def get_files_to_delete():
    """获取需要删除的文件列表"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 查询需要删除的文件（保留最新的，删除旧的）
    query = """
    SELECT 
        mf1.id,
        mf1.registration_id,
        mf1.type,
        mf1.file_name,
        mf1.file_url,
        mf1.uploaded_at
    FROM material_files mf1
    WHERE EXISTS (
        SELECT 1 
        FROM material_files mf2 
        WHERE mf2.registration_id = mf1.registration_id 
        AND mf2.type = mf1.type 
        AND mf2.id != mf1.id
    )
    AND mf1.id != (
        SELECT id FROM material_files mf3
        WHERE mf3.registration_id = mf1.registration_id 
        AND mf3.type = mf1.type 
        ORDER BY uploaded_at DESC, id DESC 
        LIMIT 1
    )
    ORDER BY mf1.registration_id, mf1.type, mf1.uploaded_at DESC
    """
    
    cursor.execute(query)
    files_to_delete = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return files_to_delete

def show_files_to_delete(files):
    """显示将要删除的文件详情"""
    print("=" * 80)
    print("以下文件将被删除（保留最新上传的文件）：")
    print("=" * 80)
    print()
    
    for i, file in enumerate(files, 1):
        print(f"{i}. ID: {file['id']}")
        print(f"   报名ID: {file['registration_id']}")
        print(f"   类型: {file['type']}")
        print(f"   文件名: {file['file_name']}")
        print(f"   MinIO路径: {file['file_url']}")
        print(f"   上传时间: {file['uploaded_at']}")
        print()

def cleanup_files(files, delete_minio=True):
    """执行清理操作"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    minio_client = None
    if delete_minio:
        try:
            minio_client = get_minio_client()
            print("[OK] MinIO client connected")
        except Exception as e:
            print(f"[WARNING] MinIO connection failed: {e}")
            print("   Will only delete database records, MinIO files need manual cleanup")
            minio_client = None
    
    print()
    print("=" * 80)
    print("开始执行清理...")
    print("=" * 80)
    print()
    
    deleted_db = 0
    deleted_minio = 0
    failed_minio = 0
    
    for file in files:
        try:
            # 删除MinIO文件
            if minio_client and file['file_url']:
                try:
                    minio_client.remove_object(MINIO_CONFIG['bucket'], file['file_url'])
                    deleted_minio += 1
                    print(f"✅ 已删除MinIO文件: {file['file_url']}")
                except Exception as e:
                    failed_minio += 1
                    print(f"⚠️  删除MinIO文件失败 {file['file_url']}: {e}")
            
            # 删除数据库记录
            cursor.execute("DELETE FROM material_files WHERE id = %s", (file['id'],))
            deleted_db += 1
            print(f"✅ 已删除数据库记录: ID={file['id']}, 报名ID={file['registration_id']}, 类型={file['type']}")
            
        except Exception as e:
            print(f"❌ 删除失败 ID={file['id']}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print()
    print("=" * 80)
    print("清理完成！")
    print("=" * 80)
    print(f"数据库记录删除: {deleted_db}")
    if delete_minio:
        print(f"MinIO文件删除: {deleted_minio}")
        if failed_minio > 0:
            print(f"MinIO删除失败: {failed_minio}")
    print()

def verify_cleanup():
    """验证清理结果"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    query = """
    SELECT 
        registration_id,
        type,
        COUNT(*) as file_count
    FROM material_files
    GROUP BY registration_id, type
    HAVING COUNT(*) > 1
    """
    
    cursor.execute(query)
    remaining_duplicates = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    print("=" * 80)
    print("清理结果验证：")
    print("=" * 80)
    
    if not remaining_duplicates:
        print("✅ 验证成功！已无重复记录。")
        print("✅ 每个报名的每种文件类型现在都只有一个文件。")
    else:
        print(f"⚠️  仍有 {len(remaining_duplicates)} 组重复记录：")
        for dup in remaining_duplicates:
            print(f"  报名ID: {dup['registration_id']}, 类型: {dup['type']}, 数量: {dup['file_count']}")
    
    print()

def main():
    """主函数"""
    print()
    print("=" * 80)
    print("材料文件重复记录清理工具")
    print("=" * 80)
    print()
    
    # 1. 分析重复情况
    duplicates = analyze_duplicates()
    if not duplicates:
        return
    
    # 2. 获取需要删除的文件
    files_to_delete = get_files_to_delete()
    
    if not files_to_delete:
        print("✅ 无需删除任何文件。")
        return
    
    # 3. 显示详情
    show_files_to_delete(files_to_delete)
    
    # 4. 确认执行
    print("=" * 80)
    print("⚠️  警告：此操作将删除旧文件，只保留最新上传的文件！")
    print("=" * 80)
    print()
    
    confirm = input("是否继续执行清理？(yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ 操作已取消")
        return
    
    delete_minio = input("是否同时删除MinIO中的文件？(yes/no): ").strip().lower()
    
    # 5. 执行清理
    cleanup_files(files_to_delete, delete_minio == 'yes')
    
    # 6. 验证结果
    verify_cleanup()
    
    print("✅ 清理流程完成！")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
