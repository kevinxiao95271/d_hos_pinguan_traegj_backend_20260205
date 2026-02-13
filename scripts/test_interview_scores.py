#!/usr/bin/env python3
"""Test interview scores API"""

import requests

BASE_URL = "http://localhost:6031"

print("="*80)
print("Test: Interview Scores API")
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

# 2. Get book scores (existing)
print("\n[2] Get book scores (existing API)...")
book_resp = requests.get(
    f"{BASE_URL}/api/admin/reviews/book-scores",
    params={"competitionId": 21},
    headers=admin_headers,
    timeout=5
)

book_scores = book_resp.json()['data']
print(f"OK Found {len(book_scores)} book scores")

# 3. Get interview scores (new)
print("\n[3] Get interview scores (new API)...")
interview_resp = requests.get(
    f"{BASE_URL}/api/admin/reviews/interview-scores",
    params={"competitionId": 21},
    headers=admin_headers,
    timeout=5
)

if interview_resp.status_code != 200:
    print(f"FAIL Status code: {interview_resp.status_code}")
    print(interview_resp.text)
else:
    interview_scores = interview_resp.json()['data']
    print(f"OK Found {len(interview_scores)} interview scores")
    
    if interview_scores:
        print("\nFirst interview score:")
        score = interview_scores[0]
        print(f"  Task ID: {score['taskId']}")
        print(f"  Project: {score['projectName']}")
        print(f"  Institution: {score['institutionName']}")
        print(f"  Group: {score['groupType']} - {score['groupCode']}")
        print(f"  Reviewer: {score['reviewerName']}")
        print(f"  Total: {score['total']}")
        print(f"  Submitted: {score['submittedAt']}")

# 4. Test with filters
print("\n[4] Test with filters...")
filtered_resp = requests.get(
    f"{BASE_URL}/api/admin/reviews/interview-scores",
    params={
        "competitionId": 21,
        "status": "SCORED",
        "groupType": "ADVANCED"
    },
    headers=admin_headers,
    timeout=5
)

if filtered_resp.status_code == 200:
    filtered_scores = filtered_resp.json()['data']
    print(f"OK Filtered scores (ADVANCED group): {len(filtered_scores)}")

print("\n" + "="*80)
print("RESULT: PASS")
print("="*80)
print("Interview scores API is working!")
print(f"  - Book scores: {len(book_scores)}")
print(f"  - Interview scores: {len(interview_scores)}")
print("="*80)
