#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Swagger UI是否可访问
"""

import sys
import io
import requests

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def check_swagger():
    """检查Swagger访问"""
    
    print("=" * 80)
    print("检查Swagger UI访问")
    print("=" * 80)
    
    # 可能的Swagger URL
    swagger_urls = [
        f"{BASE_URL}/swagger-ui.html",
        f"{BASE_URL}/swagger-ui/index.html",
        f"{BASE_URL}/swagger-ui/",
        f"{BASE_URL}/v3/api-docs"
    ]
    
    for url in swagger_urls:
        print(f"\n尝试访问: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✓ 可以访问!")
                print(f"  内容长度: {len(response.text)} 字节")
                
                # 检查是否包含swagger关键字
                if 'swagger' in response.text.lower() or 'openapi' in response.text.lower():
                    print(f"  ✓ 确认是Swagger页面")
                else:
                    print(f"  ⚠ 可能不是Swagger页面")
            elif response.status_code == 404:
                print(f"  ✗ 404 Not Found")
            elif response.status_code == 302 or response.status_code == 301:
                print(f"  → 重定向到: {response.headers.get('Location', 'unknown')}")
            else:
                print(f"  ⚠ 其他状态码")
                
        except requests.exceptions.ConnectionError:
            print(f"  ✗ 连接失败 (应用可能未启动)")
        except requests.exceptions.Timeout:
            print(f"  ✗ 请求超时")
        except Exception as e:
            print(f"  ✗ 错误: {e}")
    
    print("\n" + "=" * 80)
    print("建议:")
    print("  1. 确认应用已启动: mvn spring-boot:run")
    print("  2. 检查端口6031是否被占用")
    print("  3. 尝试访问: http://localhost:6031/swagger-ui/index.html")
    print("  4. 查看API文档: http://localhost:6031/v3/api-docs")
    print("=" * 80)

if __name__ == "__main__":
    check_swagger()
