#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

url = "http://localhost:6031/api/admin/stats/summary"
print(f"Testing: {url}")

try:
    resp = requests.get(url, timeout=5)
    print(f"Status: {resp.status_code}")
    
    data = resp.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
