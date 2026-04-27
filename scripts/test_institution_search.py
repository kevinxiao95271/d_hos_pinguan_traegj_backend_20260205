"""
机构搜索功能自测脚本
测试省级、城市、关键词等各种搜索场景
"""
import requests
import json

BASE_URL = "http://localhost:6031"

def search(region=None, keyword=None, level=None, page=0, size=5):
    body = {"page": page, "size": size}
    if region is not None:
        body["region"] = region
    if keyword is not None:
        body["keyword"] = keyword
    if level is not None:
        body["level"] = level
    resp = requests.post(f"{BASE_URL}/api/institutions/search", json=body)
    data = resp.json()
    total = data["data"]["totalElements"]
    items = data["data"]["content"]
    return total, items

def main():
    print("=" * 60)
    print("机构搜索自测")
    print("=" * 60)

    # 1. 城市下拉列表
    resp = requests.get(f"{BASE_URL}/api/institutions/cities")
    cities = resp.json()["data"]
    print(f"\n[1] 城市列表 ({len(cities)} 个): {cities}")

    # 2. 空搜索（全量）
    total, _ = search()
    print(f"\n[2] 空搜索（不传任何参数）: {total} 条")

    # 3. 省级搜索
    total, items = search(region="省级")
    print(f"\n[3] region=省级: {total} 条")
    for it in items[:3]:
        print(f"     - {it['name']} [{it['level']}]")

    # 4. 杭州市
    total, items = search(region="杭州市")
    print(f"\n[4] region=杭州市: {total} 条")
    for it in items[:3]:
        print(f"     - {it['name']} ({it['region']}) [{it['level']}]")

    # 5. 上城区（区县级）
    total, items = search(region="上城区")
    print(f"\n[5] region=上城区: {total} 条")
    for it in items[:3]:
        print(f"     - {it['name']} [{it['level']}]")

    # 6. 关键词搜索
    total, items = search(keyword="人民医院")
    print(f"\n[6] keyword=人民医院: {total} 条")
    for it in items[:3]:
        print(f"     - {it['name']} ({it['region']})")

    # 7. 关键词 + 城市组合
    total, items = search(keyword="人民", region="宁波市")
    print(f"\n[7] keyword=人民 + region=宁波市: {total} 条")
    for it in items[:3]:
        print(f"     - {it['name']} ({it['region']})")

    # 8. 关键词 + 省级
    total, items = search(keyword="浙大", region="省级")
    print(f"\n[8] keyword=浙大 + region=省级: {total} 条")
    for it in items[:3]:
        print(f"     - {it['name']} [{it['level']}]")

    print("\n" + "=" * 60)
    print("自测完成")

if __name__ == "__main__":
    main()
