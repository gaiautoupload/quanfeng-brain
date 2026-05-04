import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import requests

url = "http://localhost:8000/query"
payload = {"query": "國道第二類特殊作業收費標準"}

resp = requests.post(url, json=payload)
result = resp.json()
print(json.dumps(result, ensure_ascii=False, indent=2))
