import urllib.request
import json

APP_ID = 'cli_aa8b28a1143b1cc6'
APP_SECRET = 'ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3'
NEW_APP_TOKEN = 'ABMhb0ZXAaOGwpsYbGIc4Y2ynxe'
FB_TABLE = 'tblt6Q4YL8IxrC7i'

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

# Fix: add status field without color options (just name)
print('\n=== Fix: Add status field to feedback table ===')
try:
    r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{FB_TABLE}/fields', {
        'field_name': 'status',
        'type': 3,
        'property': {
            'options': [
                {'name': 'pending'},
                {'name': 'done'},
            ]
        }
    })
    print('status field:', r.get('code'), r.get('msg'))
except Exception as e:
    print('status field error:', e)

# Add create_time field
try:
    r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{FB_TABLE}/fields', {
        'field_name': 'create_time', 'type': 21
    })
    print('create_time field:', r.get('code'), r.get('msg'))
except Exception as e:
    print('create_time error:', e)

# ====== Create activation codes table ======
print('\n=== Create activation codes table ===')
r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables', {'table': {'name': 'activation_codes'}})
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
    for fname, ftype in [('used', 7), ('note', 1)]:
        r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{code_table_id}/fields', {
            'field_name': fname, 'type': ftype
        })
        print(f'  Code field [{fname}]:', r.get('code'), r.get('msg'))

# ====== Write scene data ======
SCENES_TABLE = 'tblWlVlgyKKjrPs7'
print('\n=== Write scene data ===')

scenes = [
    {
        'scene_name': '三里屯SOHO咖啡馆', 'category1': '室内', 'category2': '咖啡厅',
        'aperture': 'f/2.0', 'shutter': '1/125s', 'iso': '800',
        'white_balance': '4000K', 'metering': '评价测光', 'focus': '自动对焦', 'ev': '+0.3',
        'tips': '靠窗位置光线最好，避开正午直射。背景虚化选人物距离桌面1.5m以上。', 'locked': True,
        'badge': '室内·咖啡厅'
    },
    {
        'scene_name': '公园草坪黄昏', 'category1': '室外', 'category2': '公园',
        'aperture': 'f/2.8', 'shutter': '1/500s', 'iso': '200',
        'white_balance': '5500K', 'metering': '点测光', 'focus': '自动对焦', 'ev': '-0.3',
        'tips': '黄金时段前30分钟最佳，逆光拍摄注意补曝光补偿。', 'locked': False,
        'badge': '室外·公园'
    },
    {
        'scene_name': '地铁站台', 'category1': '室内', 'category2': '地铁',
        'aperture': 'f/2.0', 'shutter': '1/200s', 'iso': '1600',
        'white_balance': '3800K', 'metering': '评价测光', 'focus': '自动对焦', 'ev': '0',
        'tips': '站台灯光偏暖，白平衡手动调低偏冷可减少色偏。', 'locked': True,
        'badge': '室内·地铁'
    },
    {
        'scene_name': '街头霓虹夜景', 'category1': '室外', 'category2': '街上',
        'aperture': 'f/2.0', 'shutter': '1/60s', 'iso': '3200',
        'white_balance': 'AWB', 'metering': '评价测光', 'focus': '手动对焦', 'ev': '+0.7',
        'tips': '手持夜拍极限快门约1/60s，建议找支撑物。AWB可保留霓虹氛围色。', 'locked': True,
        'badge': '室外·夜景'
    },
    {
        'scene_name': '商场中庭', 'category1': '室内', 'category2': '商场',
        'aperture': 'f/3.5', 'shutter': '1/100s', 'iso': '640',
        'white_balance': '4200K', 'metering': '评价测光', 'focus': '自动对焦', 'ev': '+0.3',
        'tips': '玻璃幕墙反光处注意偏光，可用手遮挡镜头边缘减少鬼影。', 'locked': True,
        'badge': '室内·商场'
    },
    {
        'scene_name': '家里窗边', 'category1': '室内', 'category2': '家里',
        'aperture': 'f/2.0', 'shutter': '1/80s', 'iso': '400',
        'white_balance': '5000K', 'metering': '评价测光', 'focus': '自动对焦', 'ev': '+0.5',
        'tips': '阴天散射光最柔和，直射阳光下可用白色窗帘扩散。拍美食把物体靠近窗口。', 'locked': False,
        'badge': '室内·家里'
    },
    {
        'scene_name': '日落海边', 'category1': '室外', 'category2': '日落',
        'aperture': 'f/5.6', 'shutter': '1/1000s', 'iso': '100',
        'white_balance': '6500K', 'metering': '点测光', 'focus': '手动对焦', 'ev': '-0.7',
        'tips': '对着太阳曝光会欠曝人物，点测光对准人物后锁定曝光再构图。', 'locked': False,
        'badge': '室外·日落'
    },
    {
        'scene_name': '阴天户外街拍', 'category1': '室外', 'category2': '街上',
        'aperture': 'f/2.8', 'shutter': '1/250s', 'iso': '400',
        'white_balance': '6000K', 'metering': '评价测光', 'focus': '自动对焦', 'ev': '+0.3',
        'tips': '阴天是拍照福音，光线均匀无死角。白平衡略偏暖防止灰冷画面。', 'locked': False,
        'badge': '室外·街上'
    },
]

for s in scenes:
    # Convert locked bool to checkbox format
    fields = {}
    for k, v in s.items():
        if k == 'locked':
            fields[k] = v  # boolean for checkbox
        else:
            fields[k] = v
    r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{SCENES_TABLE}/records', {
        'fields': fields
    })
    name = s['scene_name']
    print(f'  Scene [{name}]:', r.get('code'), r.get('msg'))

# Delete empty default records
print('\n=== Clean up empty default records ===')
records = api_get(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{SCENES_TABLE}/records?page_size=50')
for rec in records.get('data', {}).get('items', []):
    if not rec.get('fields'):
        del_req = urllib.request.Request(
            f'https://open.feishu.cn/open-apis/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{SCENES_TABLE}/records/{rec["record_id"]}',
            headers={'Authorization': f'Bearer {token}'},
            method='DELETE'
        )
        try:
            with urllib.request.urlopen(del_req, timeout=15) as res:
                dr = json.loads(res.read())
            print(f'  Deleted empty record {rec["record_id"]}:', dr.get('code'))
        except Exception as e:
            print(f'  Delete error:', e)

# ====== Write activation codes ======
print('\n=== Write activation codes ===')
codes = ['CRAB-FREE-2025', 'CRAB-VIP-AAAA', 'CRAB-VIP-BBBB', 'CRAB-VIP-CCCC', 'CRAB-VIP-DDDD', 'CRAB-VIP-EEEE']
for c in codes:
    r = api_post(f'/bitable/v1/apps/{NEW_APP_TOKEN}/tables/{code_table_id}/records', {
        'fields': {'code': c, 'used': False, 'note': ''}
    })
    print(f'  Code [{c}]:', r.get('code'), r.get('msg'))

print('\n=== FINAL CONFIG ===')
print(f'APP_TOKEN = "{NEW_APP_TOKEN}"')
print(f'TBL_SCENES = "{SCENES_TABLE}"')
print(f'TBL_FEEDBACK = "{FB_TABLE}"')
print(f'TBL_CODES = "{code_table_id}"')
