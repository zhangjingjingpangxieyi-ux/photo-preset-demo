# MEMORY.md — 长期记忆

## 摄影参数速查工具（A6000拍照助手）

**产品核心定位**：图片瀑布流为主入口，用户被好看的成片吸引后点进去查参数。类Pinterest/小红书逛感，不是"查字典"式漏斗。

**页面结构**：只有两个页面——首页（瀑布流+筛选）和详情页（大图+参数+Tips+下载）。无「我的」页面。

**筛选体系**：一级（全部/室内/室外）+ 二级（咖啡厅/家里/街上/公园/地铁/商场/日落等地点词）

**付费方案**：免费8-10个高频场景，一次买断全部 ¥19.9，永久更新。付费卡片在瀑布流正常展示封面图+锁标，点进去参数区模糊遮挡。

**下载功能**：详情页下载参数卡片为图片（带品牌水印「小螃蟹的废片急诊室」），保存到相册离线用。

**内容策略**：图文笔记优先（降低创作成本），模板：参数卡片型 / 废片急诊型 / 场景教程型。小红书内容与工具双向打通，评论区高频问题 = 场景需求池。

**Demo文件**：`c:\Users\zhangjing\WorkBuddy\20260508115221\photo-preset-demo.html`（2026-05-09完成）

**飞书多维表格配置（2026-05-12 迁移至用户自建表）**：
- App ID: `cli_aa8b28a1143b1cc6`
- App Secret: `ESw5q8MugSVeaCFMpGXagdF0jrFyLJT3`
- APP_TOKEN（用户自建，wiki地址 PdKswxZK7iFb2Jk24OjcoLivnPf）: `ABMhb0ZXAaOGwpsYbGIc4Y2ynxe`
- 场景表 TBL_SCENES: `tblWlVlgyKKjrPs7`（字段均为英文，如 scene_name/category1/aperture/locked 等）
- 反馈表 TBL_FEEDBACK: `tblt6Q4YL8IxrC7i`（字段：scene_name/device/problem/wechat/status）
- 激活码表 TBL_CODES: `tblncLB5EQMGMs3U`（字段：code/used/note）
- 桥接脚本：`feishu-bridge.js`（已更新字段映射）；反馈服务器：`feedback_server.js`（已更新 app_token）
- 旧表（App自建，有权限问题）APP_TOKEN `QjRcbWiggaG9kssZjGIczGJQnGe` 已废弃
