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

def api_delete(path):
    req = urllib.request.Request(
        f'https://open.feishu.cn/open-apis{path}',
        headers={'Authorization': f'Bearer {token}'},
        method='DELETE'
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}

# Step 1: Delete old test table
print('\n--- Delete test table tblpD66C1pv1lnRU ---')
r = api_delete(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/tblpD66C1pv1lnRU')
print(json.dumps(r, ensure_ascii=False))

# Step 2: Check existing table fields
TABLE_ID = 'tblWlVlgyKKjrPs7'
print(f'\n--- List Fields in {TABLE_ID} ---')
fields = api_get(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{TABLE_ID}/fields')
print(json.dumps(fields, ensure_ascii=False, indent=2))

# Step 3: List existing records
print(f'\n--- List Records in {TABLE_ID} ---')
records = api_get(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{TABLE_ID}/records?page_size=10')
print(json.dumps(records, ensure_ascii=False, indent=2))
