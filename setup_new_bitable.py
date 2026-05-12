import urllib.request
import json

APP_ID = 'cli_aa8b28a1143b1cc6'
APP_SECRET = 'ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3'
NEW_APP_TOKEN = 'ABMhb0ZXAaOGwpsYbGIc4Y2ynxe'
OLD_TABLE = 'tblWlVlgyKKjrPs7'  # default table, will be repurposed as scenes table

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
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def api_post(path, data):
    req = urllib.request.Request(
        f'https://open.feishu.cn/open-apis{path}',
        data=json.dumps(data).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def api_put(path, data):
    req = urllib.request.Request(
        f'https://open.feishu.cn/open-apis{path}',
        data=json.dumps(data).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='PUT'
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def api_patch(path, data):
    req = urllib.request.Request(
        f'https://open.feishu.cn/open-apis{path}',
        data=json.dumps(data).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='PATCH'
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

# ====== STEP A: Rename existing table to "场景参数表" and build fields ======
print('\n=== A. Rename existing table to scenes ===')
r = api_patch(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{OLD_TABLE}', {'name': 'scene_params'})
print('Rename:', r.get('code'), r.get('msg'))

# Get existing field IDs to update them
fields = api_get(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{OLD_TABLE}/fields')
existing = fields['data']['items']
fid1 = existing[0]['field_id']  # primary
fid2 = existing[1]['field_id']  # second

print(f'Existing fields: {fid1}, {fid2}')

# Rename primary field to "场景名称"
r = api_put(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{OLD_TABLE}/fields/{fid1}', {
    'field_name': 'scene_name', 'type': 1
})
print('Field1 rename:', r.get('code'), r.get('msg'))

# Rename second field to "一级分类"
r = api_put(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{OLD_TABLE}/fields/{fid2}', {
    'field_name': 'category1', 'type': 1
})
print('Field2 rename:', r.get('code'), r.get('msg'))

# Add remaining fields
scene_fields = [
    ('category2', 1),    # 二级分类
    ('aperture', 1),     # 光圈
    ('shutter', 1),      # 快门
    ('iso', 1),          # ISO
    ('white_balance', 1),# 白平衡
    ('metering', 1),     # 测光
    ('focus', 1),        # 对焦
    ('ev', 1),           # 曝光补偿
    ('tips', 1),         # 拍摄建议
    ('cover_url', 15),   # 封面图URL (URL type=15)
    ('locked', 7),       # 付费解锁 (checkbox type=7)
    ('badge', 1),        # 标签显示
]
for fname, ftype in scene_fields:
    r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{OLD_TABLE}/fields', {
        'field_name': fname, 'type': ftype
    })
    print(f'  Add field [{fname}]:', r.get('code'), r.get('msg'))

print('\nScene table built. table_id:', OLD_TABLE)

# ====== STEP B: Create Feedback table ======
print('\n=== B. Create feedback table ===')
r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables', {
    'table': {'name': 'feedback'}
})
print('Create feedback table:', r.get('code'), r.get('msg'))
fb_table_id = r['data']['table_id'] if r.get('code') == 0 else None
print('Feedback table_id:', fb_table_id)

if fb_table_id:
    # Get auto-created primary field
    fb_fields = api_get(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{fb_table_id}/fields')
    fb_fid1 = fb_fields['data']['items'][0]['field_id']
    # Rename primary to scene_name
    r = api_put(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{fb_table_id}/fields/{fb_fid1}', {
        'field_name': 'scene_name', 'type': 1
    })
    print('  FB field1 rename:', r.get('code'))
    # Add more fields
    fb_extra = [
        ('device', 1),      # 设备型号
        ('problem', 1),     # 问题描述
        ('wechat', 1),      # 用户微信
        ('status', 3),      # 状态 (单选 type=3)
        ('create_time', 21),# 提交时间 (auto)
    ]
    for fname, ftype in fb_extra:
        extra_data = {'field_name': fname, 'type': ftype}
        if ftype == 3:
            extra_data['property'] = {
                'options': [
                    {'name': 'pending', 'color': 0},
                    {'name': 'done', 'color': 1},
                ]
            }
        r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{fb_table_id}/fields', extra_data)
        print(f'  FB field [{fname}]:', r.get('code'), r.get('msg'))

# ====== STEP C: Create activation codes table ======
print('\n=== C. Create activation codes table ===')
r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables', {
    'table': {'name': 'activation_codes'}
})
print('Create codes table:', r.get('code'), r.get('msg'))
code_table_id = r['data']['table_id'] if r.get('code') == 0 else None
print('Codes table_id:', code_table_id)

if code_table_id:
    code_fields_raw = api_get(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{code_table_id}/fields')
    code_fid1 = code_fields_raw['data']['items'][0]['field_id']
    r = api_put(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{code_table_id}/fields/{code_fid1}', {
        'field_name': 'code', 'type': 1
    })
    print('  Code field1 rename:', r.get('code'))
    code_extra = [
        ('used', 7),        # checkbox
        ('note', 1),        # 备注
        ('create_time', 21),
    ]
    for fname, ftype in code_extra:
        r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{code_table_id}/fields', {
            'field_name': fname, 'type': ftype
        })
        print(f'  Code field [{fname}]:', r.get('code'), r.get('msg'))

print('\n=== Summary ===')
print(f'APP_TOKEN: {NEW_APP_TOKEN}')
print(f'SCENES table: {OLD_TABLE}')
print(f'FEEDBACK table: {fb_table_id}')
print(f'CODES table: {code_table_id}')
