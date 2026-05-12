import urllib.request
import json

APP_ID = 'cli_aa8b28a1143b1cc6'
APP_SECRET = 'ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3'

# Step 1: Get tenant_access_token
try:
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=json.dumps({'app_id': APP_ID, 'app_secret': APP_SECRET}).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        token_data = json.loads(r.read())
    print('[Token] code:', token_data.get('code'))
    token = token_data.get('tenant_access_token', '')
    print('[Token] got:', token[:20], '...' if token else 'EMPTY')
except Exception as e:
    print('[Token] ERROR:', e)
    exit(1)

if token_data.get('code') != 0:
    print('[Token] Failed, msg:', token_data.get('msg'))
    exit(1)

# Step 2: Try wiki node API
# wiki token from URL: PdKswxZK7iFb2Jk24OjcoLivnPf
wiki_token = 'PdKswxZK7iFb2Jk24OjcoLivnPf'
url = f'https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={wiki_token}'
req2 = urllib.request.Request(
    url,
    headers={'Authorization': f'Bearer {token}'},
    method='GET'
)
try:
    with urllib.request.urlopen(req2, timeout=15) as r:
        data = json.loads(r.read())
    print('[Wiki Node]', json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print('[Wiki Node] ERROR:', e)

# Step 3: Try to search wiki pages
url3 = f'https://open.feishu.cn/open-apis/wiki/v2/spaces?page_size=10'
req3 = urllib.request.Request(
    url3,
    headers={'Authorization': f'Bearer {token}'},
    method='GET'
)
try:
    with urllib.request.urlopen(req3, timeout=15) as r:
        data3 = json.loads(r.read())
    print('[Wiki Spaces]', json.dumps(data3, ensure_ascii=False, indent=2))
except Exception as e:
    print('[Wiki Spaces] ERROR:', e)
