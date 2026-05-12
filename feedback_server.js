const http = require('http');
const https = require('https');

const APP_ID     = 'cli_aa8b28a1143b1cc6';
const APP_SECRET = 'ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3';
const APP_TOKEN  = 'ABMhb0ZXAaOGwpsYbGIc4Y2ynxe';  // 新多维表格（用户自建）
const TBL_FEEDBACK = 'tblt6Q4YL8IxrC7i';
const PORT = 3000;

function getToken(cb) {
  const body = JSON.stringify({ app_id: APP_ID, app_secret: APP_SECRET });
  const opt = {
    hostname: 'open.feishu.cn',
    path: '/open-apis/auth/v3/tenant_access_token/internal',
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': body.length }
  };
  const req = https.request(opt, res => {
    let d = '';
    res.on('data', c => d += c);
    res.on('end', () => cb(JSON.parse(d).tenant_access_token));
  });
  req.write(body);
  req.end();
}

function addFeedbackRecord(token, data, cb) {
  const body = JSON.stringify({
    fields: {
      // 字段名与新多维表格一致（英文）
      'scene_name': data.scene || '',
      'device':     data.device || '',
      'problem':    data.problem || '',
      'wechat':     data.wechat || '',
    }
  });
  const opt = {
    hostname: 'open.feishu.cn',
    path: `/open-apis/bitable/v1/apps/${APP_TOKEN}/tables/${TBL_FEEDBACK}/records`,
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Content-Length': body.length
    }
  };
  const req = https.request(opt, res => {
    let d = '';
    res.on('data', c => d += c);
    res.on('end', () => {
      const result = JSON.parse(d);
      console.log('[Feishu] Add record result:', d);
      cb(result);
    });
  });
  req.write(body);
  req.end();
}

function findSceneNameFromJSON(sceneKey, cb) {
  // Try to read scenes.json to map scene key to display name
  const fs = require('fs');
  const path = require('path');
  const jsonPath = path.join(__dirname, 'public', 'scenes.json');
  fs.readFile(jsonPath, 'utf8', (err, data) => {
    if (err) { cb(sceneKey); return; }
    try {
      const scenes = JSON.parse(data);
      if (scenes[sceneKey] && scenes[sceneKey].title) {
        cb(scenes[sceneKey].title);
      } else {
        cb(sceneKey);
      }
    } catch(e) { cb(sceneKey); }
  });
}

const server = http.createServer((req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }

  if (req.method === 'POST' && req.url === '/api/feedback') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      const data = JSON.parse(body);
      console.log('[Feedback] Received:', data);

      getToken(token => {
        // Map scene key to display name
        findSceneNameFromJSON(data.scene, sceneName => {
          addFeedbackRecord(token, { ...data, scene: sceneName }, result => {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(result));
          });
        });
      });
    });
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, () => {
  console.log(`Feedback server running at http://localhost:${PORT}`);
  console.log(`POST /api/feedback to submit feedback`);
});
