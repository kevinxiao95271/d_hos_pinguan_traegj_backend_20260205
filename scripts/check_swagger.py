# -*- coding: utf-8 -*-
"""
验证Swagger API文档是否包含所有新增接口
"""
import requests
import json

BASE_URL = "http://localhost:6031"

def check_swagger_api():
    """检查Swagger API文档"""
    print("=" * 80)
    print("检查Swagger API文档")
    print("=" * 80)
    
    # 获取OpenAPI JSON
    try:
        response = requests.get(f"{BASE_URL}/v3/api-docs", timeout=10)
        response.raise_for_status()
        api_docs = response.json()
        
        print(f"\nAPI标题: {api_docs['info']['title']}")
        print(f"版本: {api_docs['info']['version']}")
        print(f"描述: {api_docs['info']['description']}")
        
        # 检查新增的接口
        paths = api_docs.get('paths', {})
        
        print("\n" + "=" * 80)
        print("新增接口检查")
        print("=" * 80)
        
        # 用户管理接口
        print("\n【用户管理（管理员）模块】")
        user_management_endpoints = [
            ("/api/admin/users/query", "POST", "查询用户列表"),
            ("/api/admin/users/{userId}", "GET", "获取用户详情"),
            ("/api/admin/users/reviewers", "POST", "创建评委账号"),
            ("/api/admin/users/{userId}/disable", "PUT", "禁用用户"),
            ("/api/admin/users/{userId}/enable", "PUT", "启用用户"),
            ("/api/admin/users/statistics", "GET", "用户统计")
        ]
        
        for path, method, desc in user_management_endpoints:
            check_endpoint(paths, path, method.lower(), desc)
        
        # 机构模块新增接口
        print("\n【机构模块 - 新增接口】")
        institution_endpoints = [
            ("/api/institutions/search", "POST", "高性能搜索"),
            ("/api/institutions/autocomplete", "GET", "自动完成"),
            ("/api/institutions/hot-regions", "GET", "热门地区"),
            ("/api/institutions/levels", "GET", "获取所有等级"),
            ("/api/institutions/region-stats", "GET", "地区统计")
        ]
        
        for path, method, desc in institution_endpoints:
            check_endpoint(paths, path, method.lower(), desc)
        
        # 认证模块新增接口
        print("\n【认证模块 - 新增接口】")
        auth_endpoints = [
            ("/api/auth/register", "POST", "参赛者注册"),
            ("/api/auth/login-with-password", "POST", "密码登录"),
            ("/api/auth/change-password/{userId}", "POST", "修改密码")
        ]
        
        for path, method, desc in auth_endpoints:
            check_endpoint(paths, path, method.lower(), desc)
        
        # 统计所有接口
        print("\n" + "=" * 80)
        print("接口统计")
        print("=" * 80)
        total_endpoints = sum(len(methods) for methods in paths.values())
        print(f"总接口数: {total_endpoints}")
        print(f"路径数: {len(paths)}")
        
        # 按Tag分组统计
        tags_count = {}
        for path, methods in paths.items():
            for method, details in methods.items():
                tags = details.get('tags', [])
                for tag in tags:
                    tags_count[tag] = tags_count.get(tag, 0) + 1
        
        print("\n按模块统计:")
        for tag, count in sorted(tags_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {tag}: {count} 个接口")
        
        # 验证Swagger UI
        print("\n" + "=" * 80)
        print("验证Swagger UI")
        print("=" * 80)
        try:
            ui_response = requests.get(f"{BASE_URL}/swagger-ui.html", timeout=5)
            if ui_response.status_code == 200:
                print("OK Swagger UI 可访问")
                print(f"   访问地址: {BASE_URL}/swagger-ui.html")
            else:
                print(f"WARN Swagger UI 返回状态码: {ui_response.status_code}")
        except Exception as e:
            print(f"ERROR 无法访问Swagger UI: {e}")
        
        print("\n" + "=" * 80)
        print("Swagger文档验证完成！")
        print("=" * 80)
        
        return True
        
    except requests.RequestException as e:
        print(f"ERROR 无法获取API文档: {e}")
        print("   请确保服务正在运行: http://localhost:6031")
        return False
    except Exception as e:
        print(f"ERROR 解析API文档失败: {e}")
        return False

def check_endpoint(paths, path, method, description):
    """检查单个接口"""
    if path in paths and method in paths[path]:
        endpoint = paths[path][method]
        summary = endpoint.get('summary', '无')
        operation_id = endpoint.get('operationId', '无')
        print(f"OK {method.upper():6} {path}")
        print(f"       Summary: {summary}")
        print(f"       Desc: {description}")
    else:
        print(f"MISSING {method.upper():6} {path}")
        print(f"        Desc: {description}")

if __name__ == "__main__":
    check_swagger_api()
