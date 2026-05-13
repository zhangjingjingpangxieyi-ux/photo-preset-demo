/**
 * 飞书多维表格 → 本地JSON 桥接脚本
 * 运行：node feishu-bridge.js
 * 输出：public/scenes.json + public/codes.json
 *
 * 新多维表格（用户自建，app 有完整读写权限）
 */

const APP_TOKEN   = 'ABMhb0ZXAaOGwpsYbGIc4Y2ynxe';  // 用户新建的多维表格
const TBL_SCENES  = 'tblWlVlgyKKjrPs7';   // 场景参数表
const TBL_CODES   = 'tblncLB5EQMGMs3U';   // 激活码表

const APP_ID     = 'cli_aa8b28a1143b1cc6';
const APP_SECRET = 'ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3';

// ============================================================

async function getToken() {
  const r = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ app_id: APP_ID, app_secret: APP_SECRET })
  });
  const j = await r.json();
  if (j.code !== 0) throw new Error('Token error: ' + j.msg);
  return j.tenant_access_token;
}

async function api(token, method, path, body = null) {
  const opts = {
    method,
    headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' }
  };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch('https://open.feishu.cn/open-apis' + path, opts);
  return r.json();
}

/** 读取某个表的所有记录（自动翻页）*/
async function getAllRecords(token, tableId) {
  let items = [];
  let pageToken = '';
  do {
    let path = `/bitable/v1/apps/${APP_TOKEN}/tables/${tableId}/records?page_size=500`;
    if (pageToken) path += '&page_token=' + encodeURIComponent(pageToken);
    const r = await api(token, 'GET', path);
    if (r.code !== 0) { console.error('读表失败:', r); break; }
    items = items.concat(r.data.items || []);
    pageToken = r.data.has_more ? r.data.page_token : '';
  } while (pageToken);
  return items;
}

/** 把飞书记录转成前端需要的结构（匹配新字段名） */
function mapScene(rec) {
  const f = rec.fields;
  // tips 支持换行分割
  const tipsRaw = f['tips'] || '';
  const tips = tipsRaw.split('\n').map(t => t.trim()).filter(Boolean);

  return {
    id:       rec.record_id,
    title:    f['scene_name'] || '',
    badge:    f['badge'] || ((f['category1'] || '') + ' · ' + (f['category2'] || '')),
    aperture: f['aperture'] || '',
    shutter:  f['shutter'] || '',
    iso:      String(f['iso'] || ''),
    wb:       String(f['white_balance'] || ''),
    metering: f['metering'] || '',
    focus:    f['focus'] || '',
    ev:       f['ev'] || '',
    tips:     tips.length ? tips : [tipsRaw],
    locked:   f['locked'] === true || f['locked'] === 1,
    imgEmoji: '📸',
    // cover_url 在飞书里是链接类型字段，返回 { link, text }，需要取 link
    coverUrl: (f['cover_url']?.link || f['cover_url'] || f['coverUrl']?.link || f['coverUrl'] || ''),
    category1: f['category1'] || '',
    category2: f['category2'] || '',
  };
}

// ================================================================
// main

(async () => {
  console.log('[1/4] 获取 token...');
  const token = await getToken();
  console.log('  token OK');

  console.log('[2/4] 读取场景参数表...');
  const sceneRecords = await getAllRecords(token, TBL_SCENES);
  console.log(`  共 ${sceneRecords.length} 条场景记录`);

  const scenes = {};
  sceneRecords.forEach(rec => {
    const s = mapScene(rec);
    const key = s.title.replace(/\s+/g, '-').toLowerCase() || rec.record_id;
    scenes[key] = s;
  });

  console.log('[3/4] 读取激活码表...');
  const codeRecords = await getAllRecords(token, TBL_CODES);
  const codes = {};
  codeRecords.forEach(rec => {
    const f = rec.fields;
    const codeKey = f['code'];
    if (codeKey) {
      codes[codeKey] = {
        used:  f['used'] === true || f['used'] === 1,
        note:  f['note'] || '',
      };
    }
  });
  console.log(`  共 ${Object.keys(codes).length} 个激活码`);

  // 写入 JSON 文件
  const fs = require('fs');
  const path = require('path');
  const outDir = path.join(__dirname, 'public');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  fs.writeFileSync(path.join(outDir, 'scenes.json'), JSON.stringify(scenes, null, 2));
  console.log(`  OK 写入 public/scenes.json (${Object.keys(scenes).length} 条)`);

  fs.writeFileSync(path.join(outDir, 'codes.json'), JSON.stringify(codes, null, 2));
  console.log(`  OK 写入 public/codes.json (${Object.keys(codes).length} 条)`);

  console.log('\n完成！');
})().catch(err => {
  console.error('\nERROR:', err.message);
  process.exit(1);
});
