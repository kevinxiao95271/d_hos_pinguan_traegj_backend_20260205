#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UTF-8编码辅助工具
统一处理Windows下的编码问题
"""

import sys
import io
import locale

def setup_utf8_output():
    """
    设置标准输出和错误输出为UTF-8编码
    解决Windows下GBK编码导致的乱码问题
    """
    if sys.platform == "win32":
        # 设置控制台输出编码为UTF-8
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        
        # 尝试设置控制台代码页为UTF-8
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)  # UTF-8
        except:
            pass
    
    # 设置默认编码
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf-8')

def get_db_config():
    """
    获取数据库配置（UTF-8）
    """
    return {
        'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
        'port': 63606,
        'user': 'root',
        'password': 'Yiguo9527_',
        'database': 'd_hos_pinguan_traegj_20260205',
        'charset': 'utf8mb4',  # 使用utf8mb4支持完整的UTF-8字符集
        'use_unicode': True
    }

# 自动设置UTF-8输出
setup_utf8_output()
