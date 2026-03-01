import requests

BASE = "http://localhost:6031"

def search(**kwargs):
    body = {"page": 0, "size": 5, **kwargs}
    r = requests.post(f"{BASE}/api/institutions/search", json=body)
    d = r.json()["data"]
    total = d["totalElements"]
    names = [x["name"] for x in d["content"][:3]]
    return total, names

print("=== 机构搜索自测 ===\n")

# 1. city=省级
total, names = search(region="省级")
print(f"[1] city=省级: {total} 条")
for n in names: print(f"    {n}")

# 2. city=杭州市
total, names = search(region="杭州市")
print(f"\n[2] city=杭州市: {total} 条")
for n in names: print(f"    {n}")

# 3. city=杭州市 + region=上城区（前端选了市再选区）
total, names = search(region="上城区")
print(f"\n[3] city=杭州市 region=上城区: {total} 条")
for n in names: print(f"    {n}")

# 4. keyword=人民医院
total, names = search(keyword="人民医院")
print(f"\n[4] keyword=人民医院: {total} 条")
for n in names: print(f"    {n}")
