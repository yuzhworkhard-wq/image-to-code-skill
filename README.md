# Image to Code

`image-to-code` 是一个用于 Codex 的图片转代码与切图 skill，目标是把选中的 UI 图片或设计截图按 750px 画板宽度进行像素级还原，并导出独立透明 PNG 切图资源。

调用名：

```text
$image-to-code
```

## 适用场景

- 将移动端 UI 截图还原为 HTML/CSS/JS 或项目内前端代码
- 将设计图按 750px 宽度等比还原
- 从源图中提取头像、图标、插画、装饰图、导航图标等透明 PNG 资源
- 保留文本为可编辑文本层
- 将简单矩形、圆角卡片、按钮、分割线等转为原生 CSS/矢量形状
- 对切图位置、尺寸、透明背景和整页还原效果做验收

## 核心原则

- 原图是唯一视觉源，不允许凭感觉重绘或重新设计
- 画板宽度必须精确为 `750px`
- 所有元素按同一比例缩放
- 禁止自动排版、优化间距、重排布局
- 禁止用相似图标库、相似插画、AI 生成图或占位素材替代原图资源
- 切图必须来自当前源图对应区域
- 切图必须是透明背景 PNG
- 切图区域必须先通过 bbox 预览确认
- 不允许自动 trim、智能裁边、内容自适应缩边
- 交付前必须进行 bbox、PNG 透明度、贴边和整页叠图校验

## 工作流

1. 读取当前源图，记录原始尺寸。
2. 计算缩放比例：

   ```text
   scale = 750 / source_width
   final_width = 750
   final_height = round(source_height * scale)
   ```

3. 创建 `layers.manifest.json`，记录每个图层的原图 bbox、缩放后 bbox、类型、z-index 和资源路径。
4. 使用 bbox 预览脚本检查切图区域是否准确。
5. 按 manifest 从源图导出透明 PNG 切图。
6. 使用 manifest 坐标实现 750px 固定画板代码。
7. 分别验收矢量层、文本层、位图/图标切图层。
8. 截图并与 750px 原图叠图复核。

## 目录结构

```text
image-to-code/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   └── slicing.md
└── scripts/
    ├── audit_png_assets.py
    ├── compare_images.py
    ├── extract_png_asset.py
    └── preview_bboxes.py
```

## Manifest 示例

`layers.manifest.json` 示例：

```json
[
  {
    "id": "avatar",
    "type": "bitmap",
    "source_bbox": { "x": 86, "y": 112, "width": 120, "height": 120 },
    "scaled_bbox": { "x": 86, "y": 112, "width": 120, "height": 120 },
    "z_index": 10,
    "asset": "assets/images/avatar.png",
    "transparent_required": true
  },
  {
    "id": "username",
    "type": "text",
    "text": "橘子果酱",
    "source_bbox": { "x": 252, "y": 134, "width": 140, "height": 40 },
    "scaled_bbox": { "x": 252, "y": 134, "width": 140, "height": 40 },
    "font_size": 32,
    "font_weight": 700,
    "color": "#07162A",
    "z_index": 20
  }
]
```

## 脚本说明

脚本依赖：

- Pillow，许可证为 HPND License
- NumPy，许可证为 BSD-3-Clause License

安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

### 1. 预览 bbox

在源图上画出 manifest 中记录的 bbox，用于检查切图区域是否准确。

```bash
scripts/preview_bboxes.py source.png layers.manifest.json qa/bbox-preview.png --only-type bitmap
```

### 2. 按 bbox 导出 PNG

从源图按精确 bbox 导出 PNG。脚本不会自动 trim，输出画布固定等于 bbox。

```bash
scripts/extract_png_asset.py source.png assets/icons/icon-user.png \
  --x 120 --y 980 --width 72 --height 72 \
  --remove-bg floodfill \
  --manifest layers.manifest.json \
  --id icon-user
```

### 3. 审计 PNG 切图

检查 PNG 是否贴边、尺寸是否匹配，以及透明背景是否合格。

```bash
scripts/audit_png_assets.py assets/icons assets/images \
  --require-transparent-bg \
  --manifest layers.manifest.json
```

### 4. 图片差异对比

对比 750px 原图和最终渲染截图。

```bash
scripts/compare_images.py reference-750.png render-750.png --json
```

## 验收标准

- 最终画板宽度为 `750px`
- 页面布局和原图同位置、同尺寸、同层级
- 文本为可编辑文本，不 rasterize 到整页图中
- 简单图形用 CSS/原生矢量实现
- 头像、图标、插画、装饰图等从当前源图提取
- PNG 切图有 alpha 通道，背景透明
- PNG 不贴边、不缺失、不带白色或灰色矩形背景
- bbox 预览图中框选区域准确
- 最终页面截图和 750px 原图叠图无明显偏移、缺图、裁切或替代素材

## 安装

将整个目录放到 Codex 的 skills 目录：

```text
~/.codex/skills/image-to-code
```

然后在 Codex 中使用：

```text
使用 $image-to-code 将当前选中的 UI 图片转换为代码，并导出透明 PNG 切图资源。
```

## 许可证

本项目使用 MIT License 开源。详见 `LICENSE`。
