from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
print('health ->', client.get('/api/health').json())

files = {'file': ('test.txt', '这是一个用于测试的合同文本。', 'text/plain')}
resp = client.post('/api/analyze-contract', files=files)
print('status ->', resp.status_code)
print('response ->')
print(resp.text)
