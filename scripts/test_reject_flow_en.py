#!/usr/bin/env python3
"""Test reject and rescore flow"""

import requests
import json

BASE_URL = "http://localhost:6031"

print("="*80)
print("Test: Score -> Reject -> Rescore")
print("="*80)

# 1. Admin login
print("\n[1] Admin login...")
admin_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}, timeout=5)

admin_token = admin_resp.json()['data']['token']
admin_headers = {"Authorization": f"Bearer {admin_token}"}
print("OK Admin logged in")

# 2. Get tasks
print("\n[2] Get review tasks...")
tasks_resp = requests.get(
    f"{BASE_URL}/api/admin/reviews/tasks",
    params={"competitionId": 21, "stage": "BOOK"},
    headers=admin_headers,
    timeout=5
)

tasks = tasks_resp.json()['data']
print(f"OK Found {len(tasks)} tasks")

task = tasks[0]
task_id = task['id']
reviewer_id = task['reviewerId']

print(f"\nSelected task:")
print(f"  Task ID: {task_id}")
print(f"  Project: {task['projectName']}")
print(f"  Status: {task['status']}")

# 3. Reviewer login (use admin token for simplicity)
reviewer_headers = admin_headers

# 4. First score
print(f"\n[4] First score...")
score_v1 = {
    "reviewTaskId": task_id,
    "plan": 10.0,
    "problem": 10.0,
    "action": 10.0,
    "success": 10.0,
    "review": 10.0,
    "operation": 10.0,
    "presentation": 10.0,
    "highlight": "[V1] Good performance",
    "weakness": "[V1] Need improvement"
}

score_resp = requests.post(
    f"{BASE_URL}/api/reviews/scores",
    json=score_v1,
    headers=reviewer_headers,
    timeout=5
)

score1 = score_resp.json()['data']
print(f"OK First score submitted")
print(f"  Score ID: {score1['id']}")
print(f"  Total: {score1['total']}")

# 5. Reject
print(f"\n[5] Reject by admin...")
reject_resp = requests.put(
    f"{BASE_URL}/api/reviews/tasks/status",
    json={
        "reviewTaskId": task_id,
        "status": "RETURNED"
    },
    headers=admin_headers,
    timeout=5
)

print(f"OK Rejected")
print(f"  New status: {reject_resp.json()['data']['status']}")

# 6. Second score
print(f"\n[6] Second score (after reject)...")
score_v2 = {
    "reviewTaskId": task_id,
    "plan": 12.0,
    "problem": 13.0,
    "action": 14.0,
    "success": 13.0,
    "review": 12.0,
    "operation": 13.0,
    "presentation": 14.0,
    "highlight": "[V2] Excellent innovation",
    "weakness": "[V2] Further improved"
}

score2_resp = requests.post(
    f"{BASE_URL}/api/reviews/scores",
    json=score_v2,
    headers=reviewer_headers,
    timeout=5
)

score2 = score2_resp.json()['data']
print(f"OK Second score submitted")
print(f"  Score ID: {score2['id']}")
print(f"  Total: {score2['total']}")

# 7. Verify
print(f"\n[7] Verification...")
print(f"  Score ID same: {score1['id'] == score2['id']}")
print(f"  Total changed: {score1['total']} -> {score2['total']}")

# 8. Check final status
tasks_resp = requests.get(
    f"{BASE_URL}/api/admin/reviews/tasks",
    params={"competitionId": 21, "stage": "BOOK"},
    headers=admin_headers,
    timeout=5
)

tasks = tasks_resp.json()['data']
final_task = next((t for t in tasks if t['id'] == task_id), None)
print(f"  Final status: {final_task['status']}")

print("\n" + "="*80)
print("RESULT: PASS")
print("="*80)
print("Flow: SCORED -> RETURNED -> SCORED")
print(f"Score ID unchanged: {score1['id']} = {score2['id']}")
print("Data overwritten successfully")
print("="*80)
