import requests
res = requests.options('http://127.0.0.1:8001/api/v1/resume/upload', headers={
    'Origin': 'http://localhost:3000',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'Authorization'
})
print(res.status_code)
print(res.headers)
