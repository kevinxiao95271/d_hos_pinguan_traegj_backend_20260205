import json
from pathlib import Path
import requests


BASE = "http://127.0.0.1:6031"
SAMPLES = [
    "三门县人民医院",
    "东阳市人民医院",
    "丽水市中医院",
    "杭州市萧山区中医院",
    "浙江省中医院",
    "宁波市第二医院",
    "台州市中医院",
    "湖州市妇幼保健院",
]


def post_search(keyword: str, region=None, level=None):
    body = {
        "keyword": keyword,
        "region": region,
        "level": level,
        "page": 0,
        "size": 20,
        "sortBy": "name",
        "sortDirection": "ASC",
    }
    r = requests.post(f"{BASE}/api/institutions/search", json=body, timeout=20)
    r.raise_for_status()
    j = r.json()
    data = (j.get("data") or {}).get("content") or []
    return len(data), [x.get("name") for x in data[:5]]


def get_autocomplete(prefix: str):
    r = requests.get(f"{BASE}/api/institutions/autocomplete", params={"prefix": prefix}, timeout=20)
    r.raise_for_status()
    j = r.json()
    data = j.get("data") or []
    return len(data), [x.get("name") for x in data[:5]]


def main():
    miss_file = Path("D:/AiCode/cursor/d_hos_pinguan_traegj_backend_20260205/institution_miss.txt")
    print("miss_file_exists:", miss_file.exists())
    print("--- probe start ---")
    for kw in SAMPLES:
        try:
            c1, top1 = post_search(kw)
            c2, top2 = get_autocomplete(kw[:3])
            print(json.dumps({
                "keyword": kw,
                "post_search_count": c1,
                "post_search_top": top1,
                "autocomplete_prefix": kw[:3],
                "autocomplete_count": c2,
                "autocomplete_top": top2
            }, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"keyword": kw, "error": str(e)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
