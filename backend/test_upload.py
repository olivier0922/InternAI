import requests
import json

res = requests.post('http://127.0.0.1:8001/api/v1/resume/upload', headers={'Authorization': 'Bearer FAKE'}, files={'file': ('test.pdf', b'fake')})
print(res.status_code, res.text)
