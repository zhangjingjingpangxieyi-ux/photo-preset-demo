
import urllib.request, json, urllib.error, sys

APP_ID     = 'cli_aa8b28a1143b1cc6'
APP_SECRET = 'ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3'
APP_TOKEN  = 'QjRcbWiggaG9kssZjGIczGJQnGe'
USER_OPEN_ID = 'v3W6PaCiK7mkId4Cg9ghjA'

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
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body else None
    req = urllib.request.Request(
        url, data=data,
        headers={'Authorization': f'Bearer {token}',
                 'Content-Type': 'application/json; charset=utf-8'},
        method=method
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {'error': e.code, 'body': e.read().decode('utf-8')}

def log(msg):
    print(msg)
    with open('add_owner_output.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

token = get_token()
log(f'Token OK: {token[:30]}...')
BASE = 'https://open.feishu.cn/open-apis'

# From Approach2 error: "type is required"
# The `type` field should indicate the permission type.
# For Drive API v1 "members" endpoint, the body format may be:
# { "type": "bitable", "members": [{"member_type":"openid","member_id":"xxx","perm":"full_access"}] }

log('\n=== Attempt 1: Correct format with "type" field ===')
url1 = f'{BASE}/drive/v1/permissions/bitable/{APP_TOKEN}/members'
body1 = {
    'type': 'bitable',
    'members': [
        {
            'member_type': 'openid',
            'member_id': USER_OPEN_ID,
            'perm': 'full_access',
        }
    ]
}
r1 = api('POST', url1, token, body1)
log('Result: ' + json.dumps(r1, ensure_ascii=False, indent=2))

if r1.get('code', r1.get('error')) == 0:
    log('\n[SUCCESS] User added as collaborator!')
    sys.exit(0)

# Attempt 2: try with resource_path format
log('\n=== Attempt 2: resource_path format ===')
url2 = f'{BASE}/drive/v1/permissions/bitable.{APP_TOKEN}/members'
body2 = {
    'type': 'bitable',
    'members': [
        {
            'member_type': 'openid',
            'member_id': USER_OPEN_ID,
            'perm': 'full_access',
        }
    ]
}
r2 = api('POST', url2, token, body2)
log('Result: ' + json.dumps(r2, ensure_ascii=False, indent=2))

if r2.get('code', r2.get('error')) == 0:
    log('\n[SUCCESS] User added as collaborator!')
    sys.exit(0)

# Attempt 3: try PATCH (update existing)
log('\n=== Attempt 3: PATCH update ===')
url3 = f'{BASE}/drive/v1/permissions/bitable/{APP_TOKEN}/members'
body3 = {
    'type': 'bitable',
    'members': [
        {
            'member_type': 'openid',
            'member_id': USER_OPEN_ID,
            'perm': 'full_access',
        }
    ]
}
r3 = api('PATCH', url3, token, body3)
log('Result: ' + json.dumps(r3, ensure_ascii=False, indent=2))

if r3.get('code', r3.get('error')) == 0:
    log('\n[SUCCESS] User added as collaborator!')
    sys.exit(0)

# Attempt 4: Check docs - maybe it's "bitable:v1" or the permission is managed in bitable namespace
log('\n=== Attempt 4: Bitable API v1 permissions ===')
url4 = f'{BASE}/bitable/v1/apps/{APP_TOKEN}/permissions'
body4 = {
    'member_type': 'openid',
    'member_id': USER_OPEN_ID,
    'perm': 'full_access',
}
r4 = api('POST', url4, token, body4)
log('Result: ' + json.dumps(r4, ensure_ascii=False, indent=2))

if r4.get('code', r4.get('error')) == 0:
    log('\n[SUCCESS] User added as collaborator!')
    sys.exit(0)

log('\n=== All attempts done ===')
log('If still failing, please check:')
log('1. Open https://open.feishu.cn/app/cli_aa8b28a1143b1cc6')
log('2. Permissions -> enable: Drive: all permissions')
log('3. Permissions -> enable: Bitable: all permissions')
log('4. Publish the app so permissions take effect')
