import urllib.request
import json

APP_ID = 'cli_aa8b28a1143b1cc6'
APP_SECRET = 'ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3'
NEW_APP_TOKEN = 'ABMhb0ZXAaOGwpsYbGIc4Y2ynxe'

# Step 1: Get token
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=json.dumps({'app_id': APP_ID, 'app_secret': APP_SECRET}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req, timeout=15) as r:
    token_data = json.loads(r.read())
token = token_data.get('tenant_access_token', '')
print('[Token] code:', token_data.get('code'))

def api_get(path):
    req = urllib.request.Request(
        f'https://open.feishu.cn/open-apis{path}',
        headers={'Authorization': f'Bearer {token}'},
        method='GET'
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}

def api_post(path, data):
    req = urllib.request.Request(
        f'https://open.feishu.cn/open-apis{path}',
        data=json.dumps(data).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}

# Step 2: List tables in the new bitable
print('\n--- List Tables ---')
tables = api_get(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables')
print(json.dumps(tables, ensure_ascii=False, indent=2))

# Step 3: Try to create a new test table
print('\n--- Try Create Table ---')
create_result = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables', {
    'table': {
        'name': 'AI测试表'
    }
})
print(json.dumps(create_result, ensure_ascii=False, indent=2))
