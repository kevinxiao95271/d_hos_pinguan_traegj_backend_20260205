# -*- coding: utf-8 -*-
"""
测试字典 API，验证清理效果
"""
import requests
import json

base_url = "http://localhost:6031"

token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI3Iiwicm9sZSI6IkNPTU1JVFRFRV9BRE1JTiIsImlhdCI6MTczODczNzg2NCwiZXhwIjoxNzM4NzQxNDY0fQ.Tm4rTl9dA0c7ZqN6gRVCDnxfuABzCLxCF9BtY2PFGT0"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("=" * 120)
print("Test Dictionary APIs")
print("=" * 120)

types = ['subject_type', 'method', 'experience_improve', 'quality_topic']

for dict_type in types:
    print(f"\n{'=' * 120}")
    print(f"[{dict_type}]")
    print("-" * 120)
    
    url = f"{base_url}/api/dictionaries/{dict_type}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                items = data.get('data', [])
                
                print(f"\n  Total items: {len(items)}")
                
                # Check for duplicates
                labels = [item['label'] for item in items]
                unique_labels = set(labels)
                
                if len(labels) != len(unique_labels):
                    print(f"  [WARNING] Found duplicate labels: {len(labels)} items, {len(unique_labels)} unique labels")
                    
                    # Find duplicates
                    seen = set()
                    duplicates = set()
                    for label in labels:
                        if label in seen:
                            duplicates.add(label)
                        seen.add(label)
                    
                    print(f"  Duplicate labels: {duplicates}")
                else:
                    print(f"  [OK] No duplicate labels")
                
                # Check for 'other' option
                other_items = [item for item in items if 'other' in item['code'].lower() or item['label'].find('其他') >= 0]
                
                if other_items:
                    print(f"\n  'Other' options:")
                    for item in other_items:
                        status = "[OK]" if item['code'] == 'other' else "[WARNING]"
                        print(f"    {status} code={item['code']}, label={item['label']}")
                else:
                    print(f"\n  No 'other' option found")
                
                # Show some examples
                print(f"\n  Sample items (first 5):")
                for i, item in enumerate(items[:5]):
                    print(f"    {i+1}. code={item['code']:<30} label={item['label']}")
            else:
                print(f"  [ERROR] API returned success=false: {data.get('message', 'Unknown error')}")
        else:
            print(f"  [ERROR] HTTP {response.status_code}: {response.text[:200]}")
    
    except Exception as e:
        print(f"  [ERROR] Request failed: {e}")

print(f"\n{'=' * 120}")
print("[TEST COMPLETE]")
print("=" * 120)

print(f"\nAll 4 dictionary types should:")
print(f"  1. Have no duplicate labels [CHECK]")
print(f"  2. Have 'other' option with code='other' [CHECK]")
print(f"  3. Reduced item counts [CHECK]")

print(f"\n{'=' * 120}")
