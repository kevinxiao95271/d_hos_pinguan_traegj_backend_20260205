import io
import json
import sys
import urllib.request
import urllib.error
import pymysql

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "http://localhost:6031"

conn = pymysql.connect(
    host="gz-cdb-bq7gk3k5.sql.tencentcdb.com",
    port=63606,
    user="root",
    password="Yiguo9527_",
    db="d_hos_pinguan_traegj_20260205",
    charset="utf8mb4",
)
cur = conn.cursor()
cur.execute(
    "SELECT id, file_name FROM material_files WHERE LOWER(SUBSTRING_INDEX(file_name,'.',-1))='docx' ORDER BY id DESC LIMIT 1"
)
row = cur.fetchone()
conn.close()

if not row:
    print("no docx material found")
    raise SystemExit(0)

mid, name = row
print("docx material:", mid, name)

req = urllib.request.Request(
    BASE + "/api/auth/login-with-password",
    data=json.dumps({"phone": "13800000005", "password": "ops2026"}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)
token = json.loads(urllib.request.urlopen(req, timeout=8).read())["data"]["token"]

req2 = urllib.request.Request(
    BASE + f"/api/materials/{mid}/preview",
    headers={"Authorization": "Bearer " + token},
)
try:
    with urllib.request.urlopen(req2, timeout=40) as r:
        print("status:", r.status)
        print("content-type:", r.headers.get("Content-Type"))
        print("content-disposition:", r.headers.get("Content-Disposition"))
        head = r.read(5)
        print("first-bytes:", head)
except urllib.error.HTTPError as e:
    print("http error:", e.code, e.reason)
    print(e.read().decode("utf-8", errors="ignore")[:300])
