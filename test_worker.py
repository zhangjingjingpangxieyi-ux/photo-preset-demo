import urllib.request, sys

url = 'https://feishu-bridge-worker.zhangjingjingpangxieyi.workers.dev/api/scenes'
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')
try:
    r = urllib.request.urlopen(req, timeout=15)
    print('HTTP', r.status)
    print(r.read().decode()[:600])
except Exception as e:
    print('ERROR:', type(e).__name__, e)
    import traceback
    traceback.print_exc()
