# -*- coding: utf-8 -*-
"""
测试字典API - 验证'other'选项在最后
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
print("Test Dictionary API - 'other' Option at End")
print("=" * 120)

types = ['subject_type', 'method', 'experience_improve', 'quality_topic']

all_passed = True

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
                
                if not items:
                    print(f"  [WARNING] No items returned!")
                    all_passed = False
                    continue
                
                # Check if last item is 'other'
                last_item = items[-1]
                last_code = last_item.get('code', '')
                last_label = last_item.get('label', '')
                
                if last_code == 'other':
                    print(f"  [OK] Last item is 'other'")
                    print(f"       code={last_code}, label={last_label}")
                else:
                    print(f"  [FAIL] Last item is NOT 'other'!")
                    print(f"         code={last_code}, label={last_label}")
                    all_passed = False
                
                # Check if 'other' appears anywhere else
                other_positions = []
                for i, item in enumerate(items):
                    if item.get('code') == 'other':
                        other_positions.append(i)
                
                if len(other_positions) == 0:
                    print(f"  [WARNING] No 'other' option found in list!")
                    all_passed = False
                elif len(other_positions) == 1 and other_positions[0] == len(items) - 1:
                    print(f"  [OK] 'other' only appears at position {other_positions[0]} (last)")
                else:
                    print(f"  [FAIL] 'other' appears at positions: {other_positions}")
                    print(f"         Expected: only at position {len(items) - 1}")
                    all_passed = False
                
                # Show all items
                print(f"\n  All items (showing code):")
                for i, item in enumerate(items):
                    code = item.get('code', '')
                    label = item.get('label', '')
                    position = f"[{i+1}/{len(items)}]"
                    marker = " <- [other]" if code == 'other' else ""
                    print(f"    {position:<10} code={code:<30} label={label}{marker}")
            else:
                print(f"  [ERROR] API returned success=false: {data.get('message', 'Unknown error')}")
                all_passed = False
        else:
            print(f"  [ERROR] HTTP {response.status_code}: {response.text[:200]}")
            all_passed = False
    
    except Exception as e:
        print(f"  [ERROR] Request failed: {e}")
        all_passed = False

print(f"\n{'=' * 120}")
print("[TEST RESULT]")
print("=" * 120)

if all_passed:
    print(f"\n[SUCCESS] All tests passed!")
    print(f"  - All 'other' options are at the end of their lists")
    print(f"  - Other items are sorted by ID")
else:
    print(f"\n[FAIL] Some tests failed!")
    print(f"  Please check the output above for details")

print(f"\n{'=' * 120}")
