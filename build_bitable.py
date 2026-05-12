"""飞书多维表格 - 建字段+填数据"""
import urllib.request, json, time

APP_ID = "cli_aa8b28a1143b1cc6"
APP_SECRET = "ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3"
APP_TOKEN = "QjRcbWiggaG9kssZjGIczGJQnGe"

# 表ID
TBL_SCENES   = "tblHxKrHwWZNkmKH"   # 场景参数库
TBL_FEEDBACK = "tblIbv9uIsoaPdPW"   # 用户反馈收集
TBL_CODES    = "tblhGnlYn6nlfhtO"  # 兑换码管理

def get_token():
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["tenant_access_token"]

def api(method, path, token, data=None):
    url = f"https://open.feishu.cn/open-apis{path}"
    body = json.dumps(data, ensure_ascii=False).encode() if data else None
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.read().decode()[:200]}

def add_field(token, table_id, field_def):
    r = api("POST", f"/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields", token, field_def)
    code = r.get("code")
    name = field_def["field_name"]
    if code == 0: print(f"  [OK] {name}")
    elif code == 1006008: print(f"  [--] {name} (exists)")
    else: print(f"  [X] {name}: {r.get('msg')}")
    return r

def add_record(token, table_id, fields):
    r = api("POST", f"/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records", token, {"fields": fields})
    if r.get("code") == 0:
        print(f"  + {fields.get('场景名称') or fields.get('兑换码')}")
    else:
        print(f"  FAIL: {r.get('msg')}")
    return r

def delete_all_records(token, table_id):
    """先清空所有记录"""
    while True:
        r = api("GET", f"/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records?page_size=500", token)
        if r.get("code") != 0:
            print(f"  查询记录失败: {r.get('msg')}")
            break
        records = r["data"].get("items", [])
        if not records:
            break
        ids = [rec["record_id"] for rec in records]
        for rid in ids:
            api("DELETE", f"/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records/{rid}", token)
        print(f"  删除了 {len(ids)} 条记录")
        time.sleep(0.2)

token = get_token()
print(f"Token: OK\n")

# ==================== 表1: 场景参数库 ====================
print("=== 表1: 场景参数库 - 建字段 ===")
# 先查现有字段
r = api("GET", f"/bitable/v1/apps/{APP_TOKEN}/tables/{TBL_SCENES}/fields", token)
existing = [f["field_name"] for f in r.get("data", {}).get("items", [])]
print(f"  已有字段: {existing}")

# 重命名默认字段
default_fields = r["data"]["items"]
for f in default_fields:
    name = f["field_name"]
    fid = f["field_id"]
    # 重命名
    new_name = None
    if "多行文本" in name:
        new_name = "场景名称"
    elif name not in existing:
        pass
    if new_name and new_name not in existing:
        api("PUT", f"/bitable/v1/apps/{APP_TOKEN}/tables/{TBL_SCENES}/fields/{fid}", token,
            {"field_name": new_name, "type": 1})
        print(f"  rename: {name} -> {new_name}")

fields1 = [
    {"field_name": "场景名称",    "type": 1},
    {"field_name": "一级分类",    "type": 3, "property": {"options": [
        {"name": "室内"}, {"name": "室外"}
    ]}},
    {"field_name": "二级分类",    "type": 3, "property": {"options": [
        {"name": "咖啡厅"}, {"name": "家里"}, {"name": "街上"},
        {"name": "公园"}, {"name": "地铁"}, {"name": "商场"},
        {"name": "日落"}, {"name": "海边"}, {"name": "景点"}
    ]}},
    {"field_name": "封面图URL",   "type": 15},
    {"field_name": "光圈",       "type": 1},
    {"field_name": "快门",       "type": 1},
    {"field_name": "ISO",        "type": 2, "property": {"formatter": "0"}},
    {"field_name": "白平衡",     "type": 2, "property": {"formatter": "0"}},
    {"field_name": "测光模式",   "type": 3, "property": {"options": [
        {"name": "评价测光"}, {"name": "中央重点"}, {"name": "点测光"}
    ]}},
    {"field_name": "对焦模式",   "type": 3, "property": {"options": [
        {"name": "自动对焦"}, {"name": "手动对焦"}, {"name": "连续对焦"}
    ]}},
    {"field_name": "曝光补偿",   "type": 1},
    {"field_name": "焦距",       "type": 1},
    {"field_name": "是否付费",   "type": 7},
    {"field_name": "Tips",       "type": 1},
    {"field_name": "状态",       "type": 3, "property": {"options": [
        {"name": "已上线"}, {"name": "草稿"}
    ]}},
]
for f in fields1:
    if f["field_name"] not in existing:
        add_field(token, TBL_SCENES, f)
    else:
        print(f"  [--] {f['field_name']} (exists)")
    time.sleep(0.2)

# ==================== 填示例数据 ====================
print("\n=== 填示例数据 ===")
delete_all_records(token, TBL_SCENES)

scenes = [
    {
        "场景名称": "三里屯SOHO咖啡馆",
        "一级分类": "室内", "二级分类": "咖啡厅",
        "光圈": "f/2.0", "快门": "1/125s", "ISO": 800,
        "白平衡": 4000, "测光模式": "评价测光",
        "对焦模式": "自动对焦", "曝光补偿": "+0.3EV",
        "焦距": "50mm", "是否付费": True,
        "Tips": "靠窗位置光线最好，建议下午3-4点去。点一杯拿铁当道具，眼神看窗外或杯子。",
        "状态": "已上线",
    },
    {
        "场景名称": "朝阳公园日落",
        "一级分类": "室外", "二级分类": "公园",
        "光圈": "f/4.0", "快门": "1/500s", "ISO": 100,
        "白平衡": 5500, "测光模式": "评价测光",
        "对焦模式": "自动对焦", "曝光补偿": "-0.3EV",
        "焦距": "35mm", "是否付费": False,
        "Tips": "日落前30分钟黄金时段，顺光拍人。背对太阳拍剪影也好看。",
        "状态": "已上线",
    },
    {
        "场景名称": "国贸地铁站",
        "一级分类": "室内", "二级分类": "地铁",
        "光圈": "f/2.8", "快门": "1/60s", "ISO": 1600,
        "白平衡": 3200, "测光模式": "点测光",
        "对焦模式": "连续对焦", "曝光补偿": "0EV",
        "焦距": "24mm", "是否付费": False,
        "Tips": "地铁内光线复杂多变，找光源稳定的位置。抓拍比摆拍更自然。",
        "状态": "已上线",
    },
    {
        "场景名称": "五道营胡同",
        "一级分类": "室外", "二级分类": "街上",
        "光圈": "f/2.0", "快门": "1/250s", "ISO": 200,
        "白平衡": 5000, "测光模式": "评价测光",
        "对焦模式": "自动对焦", "曝光补偿": "+0.7EV",
        "焦距": "35mm", "是否付费": True,
        "Tips": "午后阳光斑驳，利用墙壁和门框做框架构图。小店门口光线通常柔和。",
        "状态": "已上线",
    },
    {
        "场景名称": "将府公园铁轨",
        "一级分类": "室外", "二级分类": "公园",
        "光圈": "f/5.6", "快门": "1/200s", "ISO": 100,
        "白平衡": 5200, "测光模式": "中央重点",
        "对焦模式": "自动对焦", "曝光补偿": "-0.3EV",
        "焦距": "50mm", "是否付费": True,
        "Tips": "早上8点前光线柔和，背景干净。铁轨线条引导构图，人物居中或三分。",
        "状态": "已上线",
    },
    {
        "场景名称": "蓝色港湾商场",
        "一级分类": "室内", "二级分类": "商场",
        "光圈": "f/2.8", "快门": "1/80s", "ISO": 640,
        "白平衡": 3600, "测光模式": "评价测光",
        "对焦模式": "自动对焦", "曝光补偿": "+0.3EV",
        "焦距": "35mm", "是否付费": True,
        "Tips": "商场灯光色温偏暖，后期可拉回正常色。找橱窗和店面结合的位置拍。",
        "状态": "已上线",
    },
    {
        "场景名称": "故宫角楼日落",
        "一级分类": "室外", "二级分类": "景点",
        "光圈": "f/8.0", "快门": "1/125s", "ISO": 100,
        "白平衡": 5600, "测光模式": "评价测光",
        "对焦模式": "自动对焦", "曝光补偿": "-0.7EV",
        "焦距": "24mm", "是否付费": True,
        "Tips": "日落前1小时人最少。构图时把水面反射和角楼结构都收进来。",
        "状态": "已上线",
    },
    {
        "场景名称": "家里窗边自然光",
        "一级分类": "室内", "二级分类": "家里",
        "光圈": "f/1.8", "快门": "1/200s", "ISO": 200,
        "白平衡": 5500, "测光模式": "评价测光",
        "对焦模式": "自动对焦", "曝光补偿": "+0.7EV",
        "焦距": "50mm", "是否付费": False,
        "Tips": "利用窗帘控制光线强度，侧光或逆光都可以。白色床单当反光板效果好。",
        "状态": "已上线",
    },
]
for scene in scenes:
    add_record(token, TBL_SCENES, scene)
    time.sleep(0.3)

# ==================== 填兑换码 ====================
print("\n=== 填兑换码 ===")
delete_all_records(token, TBL_CODES)
for code in ["DEMO2026", "CRAB001", "CRAB002", "CRAB003", "CRAB004", "CRAB005"]:
    add_record(token, TBL_CODES, {"兑换码": code, "状态": "未使用"})
    time.sleep(0.3)

print(f"\n完成！打开查看: https://my.feishu.cn/base/{APP_TOKEN}")
print(f"APP_TOKEN: {APP_TOKEN}")
print(f"场景参数库: {TBL_SCENES}")
print(f"用户反馈收集: {TBL_FEEDBACK}")
print(f"兑换码管理: {TBL_CODES}")
