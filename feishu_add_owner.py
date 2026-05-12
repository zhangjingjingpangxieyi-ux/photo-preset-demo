import urllib.request, json, urllib.error, sys

APP_ID = 'cli_aa8b28a1143b1cc6'
APP_SECRET = 'ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3'
APP_TOKEN = 'QjRcbWiggaG9kssZjGIczGJQnGe'
USER_OPEN_ID = 'v3W6PaCiK7mkId4Cg9ghjA'  # 你的 user open_id

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
        headers={'Authorization': f'Bearer {token}',
                 'Content-Type': 'application/json'},
        method=method
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'body': e.read().decode()}

def log(msg):
    with open('add_owner_output.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    print(msg, file=sys.stderr)

token = get_token()
log(f'Token OK: {token[:30]}...')
BASE = 'https://open.feishu.cn/open-apis'

# ========== 尝试多种方式添加协作者 ==========

# Approach 1: Drive v1 - add member to bitable app
log('\n=== Approach1: Drive v1 POST permissions/bitable/{token}/members ===')
url1 = f'{BASE}/drive/v1/permissions/bitable/{APP_TOKEN}/members'
body1 = {
    'member_type': 'openid',
    'member_id': USER_OPEN_ID,
    'perm': 'full_access',   # read / comment / edit / full_access
    'type': 'bitable',
}
r1 = api('POST', url1, token, body1)
log(json.dumps(r1, ensure_ascii=False, indent=2))

# Approach 2: with resource_path
log('\n=== Approach2: with resource_path as bitable.{APP_TOKEN} ===')
url2 = f'{BASE}/drive/v1/permissions/bitable.{APP_TOKEN}/members'
body2 = {
    'member_type': 'openid',
    'member_id': USER_OPEN_ID,
    'perm': 'full_access',
}
r2 = api('POST', url2, token, body2)
log(json.dumps(r2, ensure_ascii=False, indent=2))

# Approach 3: Try PATCH to update (maybe need to update existing)
log('\n=== Approach3: GET existing members first ===')
url3 = f'{BASE}/drive/v1/permissions/bitable/{APP_TOKEN}/members?page_size=20'
r3 = api('GET', url3, token)
log(json.dumps(r3, ensure_ascii=False, indent=2))

# Approach 4: Try using the "docs" endpoint (some docs say bitable is a "doc" type)
log('\n=== Approach4: docs endpoint ===')
url4 = f'{BASE}/drive/v1/docs/{APP_TOKEN}/collaborators'
body4 = {
    'collaborators': [
        {'member_type': 'openid', 'member_id': USER_OPEN_ID, 'perm': 'full'}
    ]
}
r4 = api('POST', url4, token, body4)
log(json.dumps(r4, ensure_ascii=False, indent=2))

# Approach 5: Try bitable-specific permission API
log('\n=== Approach5: bitable v1 permissions API ===')
url5 = f'{BASE}/bitable/v1/apps/{APP_TOKEN}/permissions/members'
body5 = {
    'member_type': 'openid',
    'member_id': USER_OPEN_ID,
    'perm': 'full_access',
}
r5 = api('POST', url5, token, body5)
log(json.dumps(r5, ensure_ascii=False, indent=2))

log('\n=== Done ===')
log('If all failed, we need to check app permissions in Feishu Open Platform:')
log('1. Go to https://open.feishu.cn/app/cli_aa8b28a1143b1cc6')
log('2. Go to Permissions -> Search for "Drive" and enable all Drive-related permissions')
log('3. Enable "Access bitable as app" and "Manage bitable permissions"')
