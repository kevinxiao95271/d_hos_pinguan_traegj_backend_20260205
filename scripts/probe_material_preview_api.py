import io
import json
import sys
import urllib.request
import urllib.error
import pymysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = "http://localhost:6031"
DB = dict(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    db="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4",
)


def post(path, data):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read())


def probe_preview(mid, token):
    req = urllib.request.Request(
        BASE + f"/api/materials/{mid}/preview",
        headers={"Authorization": "Bearer " + token},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            print("preview status:", r.status)
            print("content-type:", r.headers.get("Content-Type"))
            print("content-disposition:", r.headers.get("Content-Disposition"))
    except urllib.error.HTTPError as e:
        print("preview failed:", e.code, e.reason)
        print(e.read().decode("utf-8", errors="ignore")[:200])


conn = pymysql.connect(**DB)
cur = conn.cursor()
cur.execute("SELECT id, file_name FROM material_files ORDER BY id DESC LIMIT 1")
row = cur.fetchone()
conn.close()
if not row:
    print("no material_files data")
    raise SystemExit(0)

material_id, file_name = row
print("material_id:", material_id, "file:", file_name)

login = post("/api/auth/login-with-password", {"phone": "13800000005", "password": "ops2026"})
token = login["data"]["token"]
probe_preview(material_id, token)
