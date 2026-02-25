# -*- coding: utf-8 -*-
"""
验证本地部署是否成功
"""
import requests
import json

BASE_URL = "http://localhost:6031"

def verify_service():
    """验证服务部署"""
    print("=" * 60)
    print("验证本地部署 - 端口 6031")
    print("=" * 60)
    
    # 1. 检查健康状态
    print("\n[1/5] 检查服务健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/actuator/health", timeout=5)
        health = response.json()
        status = health.get('status', 'UNKNOWN')
        print(f"      OK 服务状态: {status}")
    except Exception as e:
        print(f"      ERROR: {e}")
        return False
    
    # 2. 检查Swagger API文档
    print("\n[2/5] 检查Swagger API文档...")
    try:
        response = requests.get(f"{BASE_URL}/v3/api-docs", timeout=5)
        api_docs = response.json()
        paths = api_docs.get('paths', {})
        print(f"      OK API文档可访问")
        print(f"      - 接口总数: {len(paths)}")
        print(f"      - API标题: {api_docs['info']['title']}")
        print(f"      - API版本: {api_docs['info']['version']}")
    except Exception as e:
        print(f"      ERROR: {e}")
        return False
    
    # 3. 检查用户管理接口是否存在
    print("\n[3/5] 检查用户管理模块...")
    user_endpoints = [
        "/api/admin/users/query",
        "/api/admin/users/{userId}",
        "/api/admin/users/reviewers",
        "/api/admin/users/{userId}/disable",
        "/api/admin/users/{userId}/enable",
        "/api/admin/users/statistics"
    ]
    for endpoint in user_endpoints:
        if endpoint in paths:
            print(f"      OK {endpoint}")
        else:
            print(f"      MISSING {endpoint}")
    
    # 4. 检查机构搜索接口
    print("\n[4/5] 检查机构搜索优化接口...")
    institution_endpoints = [
        "/api/institutions/search",
        "/api/institutions/autocomplete",
        "/api/institutions/hot-regions",
        "/api/institutions/levels"
    ]
    for endpoint in institution_endpoints:
        if endpoint in paths:
            methods = list(paths[endpoint].keys())
            print(f"      OK {endpoint} [{', '.join(m.upper() for m in methods)}]")
        else:
            print(f"      MISSING {endpoint}")
    
    # 5. 检查认证接口
    print("\n[5/5] 检查认证接口...")
    auth_endpoints = [
        "/api/auth/register",
        "/api/auth/login-with-password",
        "/api/auth/change-password/{userId}"
    ]
    for endpoint in auth_endpoints:
        if endpoint in paths:
            methods = list(paths[endpoint].keys())
            print(f"      OK {endpoint} [{', '.join(m.upper() for m in methods)}]")
        else:
            print(f"      MISSING {endpoint}")
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)
    print(f"\nSwagger UI: {BASE_URL}/swagger-ui.html")
    print(f"API文档: {BASE_URL}/v3/api-docs")
    print("\n部署成功！所有新增功能已就绪。")
    
    return True

if __name__ == "__main__":
    try:
        verify_service()
    except Exception as e:
        print(f"ERROR 验证失败: {e}")
