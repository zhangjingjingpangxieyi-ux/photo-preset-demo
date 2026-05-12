# 场景封面图使用说明

## 两种添加方式（任选一种）

### 方式一：放本地图片文件（推荐）
1. 把图片文件放到 `public/images/` 目录下
2. 图片文件名随意，比如 `cafe-1.jpg`、`street-night.png`
3. 在飞书多维表格里，找到对应场景行，在 `cover` 字段填写文件名（如 `cafe-1.jpg`）
4. 前端会自动拼接路径 `public/images/cafe-1.jpg` 来显示图片

### 方式二：填图片链接
1. 把图片上传到图床（如 GitHub、飞书文档、微博图床等）
2. 复制图片的直接访问链接（以 `.jpg/.png/.webp` 结尾）
3. 在飞书多维表格里，在 `cover_url` 字段填写完整链接
4. 前端会直接用这个链接显示图片

> `cover_url` 优先级高于 `cover`，两个都填了会优先用 `cover_url`

## 图片规格建议
- 格式：JPG / PNG / WebP
- 尺寸：宽 375px 以上（手机端显示）
- 大小：建议 ≤ 500KB，避免加载慢
- 比例：3:4 或 1:1 竖图最佳（瀑布流展示效果好）

## 示例
假设你要为「咖啡厅·下午」场景加封面图：
1. 图片文件命名为 `cafe-afternoon.jpg`
2. 放到 `public/images/cafe-afternoon.jpg`
3. 飞书表对应行的 `cover` 字段填 `cafe-afternoon.jpg`
4. 推送到 GitHub，等待 1-2 分钟，图片就会显示在小程序里
