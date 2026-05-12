"""只处理分享权限"""
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

def api_raw(method, path, token, data=None):
    url = f"https://open.feishu.cn/open-apis{path}"
    body = json.dumps(data, ensure_ascii=False).encode() if data else None
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, method=method)
    with urllib.request.urlopen(req) as r:
        raw = r.read()
        print(f"RAW: {raw[:200]}")
        return json.loads(raw)

token = get_token()

# 先查询已有的应用
print("=== 查询已创建的应用 ===")
r = api_raw("GET", "/open-apis/application/v6/applications?page_size=10", token)
print(json.dumps(r, ensure_ascii=False, indent=2))
