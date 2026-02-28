#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化系统模版到 MinIO
将根目录的两个 .docx 文件上传到 MinIO 并在数据库中创建记录
"""

import pymysql
from pathlib import Path
from minio import Minio
from minio.error import S3Error
import uuid

# 数据库配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hos_pinguan_traegj_20260205',
    'charset': 'utf8mb4'
}

# MinIO 配置
MINIO_CONFIG = {
    'endpoint': '119.167.165.27:58010',
    'access_key': 'minioadmin',
    'secret_key': 'Ygcx2025',
    'secure': False  # HTTP
}

BUCKET_NAME = 'system-templates'

# 模版文件配置（文件在 docs 目录）
TEMPLATE_FILES = [
    {
        'source': 'docs/2026浙江省医院品管大赛报名表模板.docx',
        'type': 'registration_form'
    },
    {
        'source': 'docs/成果报告相关说明.docx',
        'type': 'result_report'
    }
]

def init_minio_client():
    """初始化 MinIO 客户端"""
    print("Initializing MinIO client...")
    return Minio(
        MINIO_CONFIG['endpoint'],
        access_key=MINIO_CONFIG['access_key'],
        secret_key=MINIO_CONFIG['secret_key'],
        secure=MINIO_CONFIG['secure']
    )

def ensure_bucket_exists(client):
    """确保 bucket 存在"""
    try:
        if not client.bucket_exists(BUCKET_NAME):
            client.make_bucket(BUCKET_NAME)
            print(f"Created bucket: {BUCKET_NAME}")
        else:
            print(f"Bucket already exists: {BUCKET_NAME}")
    except S3Error as e:
        print(f"Error ensuring bucket: {e}")
        raise

def upload_to_minio(client, file_path, object_name):
    """上传文件到 MinIO"""
    try:
        client.fput_object(
            BUCKET_NAME,
            object_name,
            str(file_path),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        print(f"  Uploaded to MinIO: {object_name}")
        return True
    except S3Error as e:
        print(f"  Error uploading {object_name}: {e}")
        return False

def insert_db_record(conn, template_info):
    """插入数据库记录"""
    cursor = conn.cursor()
    try:
        sql = """
        INSERT INTO system_template_files 
        (template_type, file_name, minio_object_name, file_size, version, is_active, uploaded_at)
        VALUES (%s, %s, %s, %s, 1, TRUE, NOW())
        """
        cursor.execute(sql, (
            template_info['type'],
            template_info['file_name'],
            template_info['object_name'],
            template_info['file_size']
        ))
        conn.commit()
        print(f"  DB record created for: {template_info['file_name']}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"  Error inserting DB record: {e}")
        return False
    finally:
        cursor.close()

def main():
    print("=" * 70)
    print("System Template Initialization Script (MinIO Version)")
    print("=" * 70)
    
    # 获取项目根目录（脚本所在目录的父目录）
    project_root = Path(__file__).parent.parent
    print(f"\nProject root: {project_root}")
    
    # 1. 初始化 MinIO 客户端
    print("\n[Step 1/4] Initializing MinIO client...")
    try:
        minio_client = init_minio_client()
        print("MinIO client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize MinIO client: {e}")
        return
    
    # 2. 确保 bucket 存在
    print("\n[Step 2/4] Ensuring bucket exists...")
    try:
        ensure_bucket_exists(minio_client)
    except Exception as e:
        print(f"Failed to ensure bucket: {e}")
        return
    
    # 3. 连接数据库
    print("\n[Step 3/4] Connecting to database...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("Database connected successfully")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return
    
    # 4. 处理每个模版文件
    print("\n[Step 4/4] Processing template files...")
    success_count = 0
    
    # 自动查找 docs 目录下的 docx 文件
    docs_dir = project_root / 'docs'
    docx_files = list(docs_dir.glob('*.docx'))
    
    print(f"Found {len(docx_files)} docx files in docs directory")
    
    if len(docx_files) == 0:
        print("  WARNING: No docx files found in docs directory")
        conn.close()
        return
    
    # 根据文件名判断类型
    file_type_mapping = {
        '报名表': 'registration_form',
        '成果报告': 'result_report'
    }
    
    for source_path in docx_files:
        print(f"\nProcessing: {source_path.name}")
        
        # 判断文件类型
        file_type = None
        for keyword, ftype in file_type_mapping.items():
            if keyword in source_path.name:
                file_type = ftype
                break
        
        if file_type is None:
            print(f"  WARNING: Cannot determine template type, skipping")
            continue
        
        # 生成 MinIO 对象名称
        object_name = f"{file_type}/{uuid.uuid4()}-{source_path.name}"
        print(f"  Type: {file_type}")
        print(f"  Object name: {object_name}")
        
        # 上传到 MinIO
        if upload_to_minio(minio_client, source_path, object_name):
            # 插入数据库记录
            template_info = {
                'type': file_type,
                'file_name': source_path.name,
                'object_name': object_name,
                'file_size': source_path.stat().st_size
            }
            
            if insert_db_record(conn, template_info):
                success_count += 1
                print(f"  SUCCESS: {source_path.name}")
    
    # 5. 清理
    conn.close()
    
    # 6. 总结
    print("\n" + "=" * 70)
    print(f"Initialization completed! Processed {success_count}/{len(docx_files)} templates")
    print("=" * 70)
    
    # 7. 验证
    print("\nVerification:")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, template_type, file_name, version, is_active, 
               LEFT(minio_object_name, 50) as object_name_preview
        FROM system_template_files
    """)
    rows = cursor.fetchall()
    
    if rows:
        print(f"\nDatabase records (total: {len(rows)}):")
        for row in rows:
            print(f"  ID={row[0]}, Type={row[1]}, File={row[2]}, Ver={row[3]}, Active={row[4]}")
            print(f"    Object: {row[5]}...")
    else:
        print("  No records found in database")
    
    cursor.close()
    conn.close()
    
    print("\nDone!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
