import urllib.request, json

APP_ID = "cli_aa8b28a1143b1cc6"
APP_SECRET = "ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3"

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
        return {"code": e.code, "msg": e.read().decode()[:300]}

token = get_token()

# 直接用第一个脚本记录的token查
# 第一次创建成功的token
tokens_to_try = [
    "QjRcbWiggaHokssZjGIczGJQnGe",  # 第一次输出
    "QjRcbWiggaH9kssZjGIczGJQnGe",  # 第二次输出
]

for t in tokens_to_try:
    print(f"\n=== 尝试 token: {t} ===")
    r = api("GET", f"/bitable/v1/apps/{t}/tables", token)
    print(f"code={r.get('code')}, msg={r.get('msg')}")
    if r.get("code") == 0:
        tables = r["data"]["items"]
        for tbl in tables:
            print(f"  table: {tbl['name']} -> {tbl['table_id']}")
