/**
 * 飞书多维表格 API 代理 Worker
 * 
 * 部署后提供两个端点：
 *   GET /api/scenes  → 返回 { scenes: {...} }
 *   GET /api/codes   → 返回 { codes: {...} }
 *
 * 环境变量（在 Cloudflare Dashboard 设置）：
 *   FEISHU_APP_ID     = cli_aa8b28a1143b1cc6
 *   FEISHU_APP_SECRET = ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3
 *   FEISHU_APP_TOKEN  = ABMhb0ZXAaOGwpsYbGIc4Y2ynxe
 *   TBL_SCENES        = tblWlVlgyKKjrPs7
 *   TBL_CODES         = tblncLB5EQMGMs3U
 */

// 飞书配置（fallback，默认值）
const FEISHU_APP_ID    = FEISHU_APP_ID    || 'cli_aa8b28a1143b1cc6';
const FEISHU_APP_SECRET= FEISHU_APP_SECRET|| 'ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3';
const FEISHU_APP_TOKEN = FEISHU_APP_TOKEN || 'ABMhb0ZXAaOGwpsYbGIc4Y2ynxe';
const TBL_SCENES       = TBL_SCENES       || 'tblWlVlgyKKjrPs7';
const TBL_CODES        = TBL_CODES        || 'tblncLB5EQMGMs3U';

const FEISHU_API = 'https://open.feishu.cn/open-apis';
const CACHE_TTL = 60; // 缓存 60 秒，避免频繁调用

// ============================================================
// 工具函数
// ============================================================

async function getFeishuToken() {
  const r = await fetch(`${FEISHU_API}/auth/v3/tenant_access_token/internal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ app_id: FEISHU_APP_ID, app_secret: FEISHU_APP_SECRET })
  });
  const j = await r.json();
  if (j.code !== 0) throw new Error('Token error: ' + j.msg);
  return j.tenant_access_token;
}

async function feishuGet(token, path) {
  const r = await fetch(`${FEISHU_API}${path}`, {
    headers: { 'Authorization': 'Bearer ' + token }
  });
  return r.json();
}

async function getAllRecords(token, tableId) {
  let items = [];
  let pageToken = '';
  do {
    let path = `/bitable/v1/apps/${FEISHU_APP_TOKEN}/tables/${tableId}/records?page_size=500`;
    if (pageToken) path += '&page_token=' + encodeURIComponent(pageToken);
    const r = await feishuGet(token, path);
    if (r.code !== 0) throw new Error('读表失败: ' + r.msg);
    items = items.concat(r.data.items || []);
    pageToken = r.data.has_more ? r.data.page_token : '';
  } while (pageToken);
  return items;
}

function mapScene(rec) {
  const f = rec.fields;
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
    // 飞书链接类型字段返回 { link, text }，需要取 link
    coverUrl: (f['cover_url']?.link || f['cover_url'] || f['coverUrl']?.link || f['coverUrl'] || ''),
    category1: f['category1'] || '',
    category2: f['category2'] || '',
  };
}

// ============================================================
// 请求处理
// ============================================================

async function handleApi(request) {
  const url = new URL(request.url);
  const path = url.pathname;

  // CORS 头（允许 H5 跨域调用）
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const token = await getFeishuToken();

    if (path === '/api/scenes') {
      // 尝试从缓存读
      const cacheKey = 'scenes-v1';
      const cache = caches.default;
      let cached = await cache.match(url);
      if (cached) {
        return new Response(cached.body, {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      const records = await getAllRecords(token, TBL_SCENES);
      const scenes = {};
      records.forEach(rec => {
        const s = mapScene(rec);
        const key = s.title.replace(/\s+/g, '-').toLowerCase() || rec.record_id;
        scenes[key] = s;
      });

      const body = JSON.stringify({ scenes });
      const response = new Response(body, {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
      // 写入缓存
      response.headers.set('Cache-Control', `max-age=${CACHE_TTL}`);
      return response;
    }

    if (path === '/api/codes') {
      const records = await getAllRecords(token, TBL_CODES);
      const codes = {};
      records.forEach(rec => {
        const f = rec.fields;
        const codeKey = f['code'];
        if (codeKey) {
          codes[codeKey] = {
            used: f['used'] === true || f['used'] === 1,
            note: f['note'] || '',
          };
        }
      });
      return new Response(JSON.stringify({ codes }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // 未知路径
    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

// ============================================================
// Worker 入口
// ============================================================

export default {
  async fetch(request, env, ctx) {
    return handleApi(request);
  }
};
