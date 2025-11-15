from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
print('health ->', client.get('/api/health').json())

# simulate bytes that start with BOM then utf-8 text
payload = b"\xef\xbb\xbf" + '这是一个用于测试的合同文本（含 BOM）。'.encode('utf-8')
files = {'file': ('test.txt', payload, 'application/octet-stream')}
resp = client.post('/api/analyze-contract', files=files)
print('status ->', resp.status_code)
print('response ->')
print(resp.text)
