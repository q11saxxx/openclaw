import json
import urllib.request

payload = {"skill_id": "597d6a1eb97b48cca31a4007700003d8"}
data = json.dumps(payload).encode()
req = urllib.request.Request('http://localhost:8000/audits/run', data=data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req).read().decode()
print(resp)
