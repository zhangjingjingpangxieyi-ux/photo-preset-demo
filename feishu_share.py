import urllib.request, json, sys

APP_ID = 'cli_aa8b28a1143b1cc6'
APP_SECRET = 'ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3'
APP_TOKEN = 'QjRcbWiggaG9kssZjGIczGJQnGe'

def get_token():
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=json.dumps({'app_id': APP_ID, 'app_secret': APP_SECRET}).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
    return resp['tenant_access_token']

def api(method, url, token, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method=method
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'body': e.read().decode()}

def log(msg):
    with open('share_output.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

token = get_token()
log(f'Token OK: {token[:20]}...')

BASE = 'https://open.feishu.cn/open-apis'

# Approach 1: Drive v1 API - set bitable app public read
log('\n=== Approach1: Drive v1 - POST permissions/bitable/{token}/public ===')
url1 = f'{BASE}/drive/v1/permissions/bitable/{APP_TOKEN}/public'
body1 = {'perm': 'read', 'type': 'anyone'}
result1 = api('POST', url1, token, body1)
log(json.dumps(result1, ensure_ascii=False, indent=2))

# Approach 2: Drive v1 API - PATCH (update existing share)
log('\n=== Approach2: Drive v1 - PATCH permissions/bitable/{token}/public ===')
url2 = f'{BASE}/drive/v1/permissions/bitable/{APP_TOKEN}/public'
body2 = {'perm': 'read', 'type': 'anyone'}
result2 = api('PATCH', url2, token, body2)
log(json.dumps(result2, ensure_ascii=False, indent=2))

# Approach 3: Try with resource_path parameter
log('\n=== Approach3: Drive v1 - with resource_path ===')
url3 = f'{BASE}/drive/v1/permissions/bitable.{APP_TOKEN}/public'
body3 = {'perm': 'read', 'type': 'anyone'}
result3 = api('POST', url3, token, body3)
log(json.dumps(result3, ensure_ascii=False, indent=2))

# Approach 4: Check Feishu Open API docs - the correct API might be in bitable namespace
# According to some docs: POST /bitable/v1/apps/{app_token}/shares
# But we got 404. Let's try GET to list shares first.
log('\n=== Approach4: GET existing shares (bitable API) ===')
url4 = f'{BASE}/bitable/v1/apps/{APP_TOKEN}/shares?page_size=20'
result4 = api('GET', url4, token)
log(json.dumps(result4, ensure_ascii=False, indent=2))

# Approach 5: Create share via bitable API (different body format)
log('\n=== Approach5: POST create share - correct body format ===')
url5 = f'{BASE}/bitable/v1/apps/{APP_TOKEN}/shares'
body5 = {
    'share_type': 'public',   # public / tenant / invite
    'permission': 'read',
}
result5 = api('POST', url5, token, body5)
log(json.dumps(result5, ensure_ascii=False, indent=2))

log('\nDone. If all failed, please set in Feishu UI:')
log('Open base -> Click Share button (top-right) -> Set link permission to "Anyone with link can read"')
