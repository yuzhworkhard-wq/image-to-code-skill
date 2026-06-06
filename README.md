# Image to Code

`image-to-code` is a Codex skill for turning a selected UI image, screenshot, or Figma export into an adaptive code implementation, high-density transparent PNG assets, and optional editable Figma layer output.

`750px` is the baseline coordinate system used for measurement and QA. It is not the only final display width. The final production output should include a responsive fit wrapper that scales the locked 750px artboard to mobile viewports or embedding containers without reflowing individual layers.

`image-to-code` 是一个用于 Codex 的图片转代码 skill：它把选中的 UI 图片、截图或 Figma 导出稿还原为最终可自适应展示的代码，同时导出 2x/3x/4x 高清透明 PNG 切图资源，并可在后续拆分为可编辑 Figma 图层。

`750px` 是测量、定位和复核用的基准坐标系，不是最终页面唯一显示宽度。最终生产代码必须在保持 750px 基准稿可精确复核的前提下，通过外层 fit wrapper 按手机视口或容器宽度整体等比缩放。

## Contents

- [中文说明](#中文说明)
- [English Guide](#english-guide)
- [Repository Structure](#repository-structure)
- [License](#license)

## 中文说明

### 核心定位

这个项目不是普通前端模板，也不是“重新设计”工具。它是一套 Codex skill 工作流，用来约束图片转代码任务中的测量、切图、代码、响应式适配、QA 和 Figma 后续导入。

核心产出包括：

- 自适应前端代码：以 750px 锁定画板为基准，外层整体缩放适配 `320px-430px` 手机宽度、375px 演示宽度或指定容器宽度。
- 独立高清 PNG 资源：图标、头像、插画、复杂装饰、产品图等从当前源图切出，默认 2x，必要时 3x 或 4x。
- `layers.manifest.json`：记录每个图层的源图 bbox、750px 基准 bbox、z-index、资源路径、PNG 像素尺寸和 CSS 显示尺寸。
- 透明背景与防裁切 QA：bbox 预览、PNG alpha 审计、棋盘格/黑底/白底检查、整页截图差异对比。
- 可选 Figma 输出：代码与 QA 完成后，可按同一份 manifest/code/assets 拆成 Figma text node、shape、image fill 和本地 importer。

### 安装方式

把整个目录放到 Codex 的 skills 目录：

```text
~/.codex/skills/image-to-code
```

安装脚本依赖：

```bash
python3 -m pip install -r requirements.txt
```

当前脚本依赖 Pillow 和 NumPy。

### 如何触发

在 Codex 中点名 skill：

```text
使用 $image-to-code 将当前选中的 UI 图片转换为自适应代码，并导出透明 PNG 切图资源。
```

也可以自然描述：

```text
把这张移动端设计图还原成 HTML/CSS，最终页面要自适应手机宽度，图标和插画请按 2x/3x 单独切成透明 PNG，后面还要能导入 Figma。
```

### 750px 基准与自适应最终产物

`750px` 的作用是建立稳定的设计坐标系：

```text
scale = 750 / source_width
baseline_width = 750
baseline_height = round(source_height * scale)
scaled_x = source_x * scale
scaled_y = source_y * scale
scaled_width = source_width_of_layer * scale
scaled_height = source_height_of_layer * scale
```

同一个缩放比例应用到坐标、宽高、圆角、描边、阴影、字体和渐变位置。这个 750px 版本用于精确复核和截图对比。

最终页面还必须提供自适应外层：

- `.artboard` 或等效根画板保持 `width: 750px` 和归一化高度。
- 所有子图层继续使用 manifest 中的 750px 基准坐标，不重新排版。
- 外层 wrapper 根据容器或视口计算 `scale = min(1, availableWidth / 750)`。
- wrapper 的实际占位宽高同步缩放，避免未缩放的 750px 内容撑开页面。
- 375px 手机演示时，常见缩放比例约为 `0.5`；还需要检查至少一个其他手机宽度。

推荐结构：

```html
<main class="fit-shell">
  <div class="fit-box">
    <section class="artboard">...</section>
  </div>
</main>
```

```css
:root {
  --board-w: 750;
  --board-h: 1624;
  --board-scale: min(1, calc(100vw / (var(--board-w) * 1px)));
}

.fit-shell {
  width: 100%;
  display: grid;
  place-items: start center;
  overflow-x: clip;
}

.fit-box {
  width: calc(var(--board-w) * 1px * var(--board-scale));
  height: calc(var(--board-h) * 1px * var(--board-scale));
  overflow: hidden;
}

.artboard {
  position: relative;
  width: calc(var(--board-w) * 1px);
  height: calc(var(--board-h) * 1px);
  transform: scale(var(--board-scale));
  transform-origin: top left;
}
```

如果需要按父容器而不是视口适配，可以用 `ResizeObserver` 设置 `--board-scale`。无论哪种方式，750px QA 截图时都应能让缩放比例回到 `1`。

### 标准工作流程

1. **检查输入图和项目约束**

   确认源图尺寸、目标技术栈、是否需要代码加切图、哪些文字要可编辑、哪些复杂图形要保留为 PNG、最终展示宽度和是否需要 Figma 输出。

2. **归一化到 750px 基准画板**

   计算统一缩放比例，建立 `750px x baseline_height` 的 QA 坐标系。

3. **建立 `layers.manifest.json`**

   manifest 是布局、切图、代码和 Figma 导出的共同数据源。不要先写近似页面再补图。

4. **预览 bbox**

   切图前先在源图上画出每个资源 bbox：

   ```bash
   scripts/preview_bboxes.py source.png layers.manifest.json qa/bbox-preview.png --only-type bitmap
   ```

5. **按 2x/3x/4x 导出高清 PNG**

   使用 `asset_scale_factor` 放大文件真实像素，同时保持页面 CSS 显示尺寸等于原元素外框。

6. **实现 750px 锁定画板**

   文本和简单图形尽量代码化，复杂图标/插画/头像/产品图使用独立 PNG 图层。每个关键图层都应能追溯到 manifest。

7. **增加自适应 fit wrapper**

   在完成 750px 基准稿后单独做手机端适配。适配只发生在外层整体缩放，不改变子元素坐标、字号、间距或尺寸。

8. **分模块 QA**

   分别检查文本层、矢量/规则图形、PNG 位图/图标资源。

9. **截图复核**

   截 750px 基准图，与归一化原图对比；再截 375px 和至少一个其他手机宽度，检查无横向滚动、无溢出、无未缩放 750px 内容撑开页面。

10. **可选导出 Figma**

   代码和 QA 完成后，如果用户要求 Figma，基于 manifest/code/assets 生成可编辑 Figma 图层规格或本地 importer。

### Manifest 示例

`asset_pixel_width/height` 是 PNG 文件真实像素尺寸；`css_display_width/height` 是页面和 Figma 中显示的尺寸。2x/3x/4x 不会改变布局占位。

```json
[
  {
    "id": "icon-home-01",
    "type": "bitmap",
    "source_bbox": { "x": 120, "y": 88, "width": 32, "height": 32 },
    "scaled_bbox": { "x": 120, "y": 88, "width": 32, "height": 32 },
    "z_index": 12,
    "asset": "assets/icons/icon-home-01.png",
    "asset_pixel_width": 96,
    "asset_pixel_height": 96,
    "asset_scale_factor": 3,
    "css_display_width": 32,
    "css_display_height": 32,
    "transparent_required": true,
    "notes": "3x 高清导出，页面仍按 32x32 显示"
  },
  {
    "id": "title-name",
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

### 高清切图与透明 PNG

切图的原则是“高清文件、固定显示、透明背景、不裁边”：

- `asset_scale_factor` 默认至少 `2`。
- 小于 `64px` 的图标、源图压缩明显、边缘脏、抠底困难或页面里发糊时用 `3` 或 `4`。
- `asset_pixel_width = css_display_width * asset_scale_factor`。
- `asset_pixel_height = css_display_height * asset_scale_factor`。
- 代码里的 `<img>` 或背景图必须按 `css_display_width/css_display_height` 显示，不能因为 PNG 是 3x 就撑大布局。
- 背景抠除应在高清画布里完成，不能先低清抠图失败后直接放大。
- PNG 不能自动 trim，不能按可见主体缩边，必须保留透明留白和半透明边缘。
- `assets/icons/` 和 `assets/illustrations/` 默认都要求透明背景，除非 manifest 明确说明它是照片、截图或完整矩形背景素材。

推荐命令：

```bash
scripts/extract_png_asset.py source.png assets/icons/icon-home-01.png \
  --x 120 --y 88 --width 32 --height 32 \
  --scale-factor 3 \
  --css-width 32 --css-height 32 \
  --remove-bg floodfill \
  --manifest layers.manifest.json \
  --id icon-home-01
```

审计 PNG：

```bash
scripts/audit_png_assets.py assets/icons assets/illustrations assets/images \
  --require-transparent-bg \
  --manifest layers.manifest.json
```

如果审计发现 `has_alpha_channel=false`、`transparent_bg_ok=false`、四角 alpha 不透明、或非透明像素贴边，应扩大 bbox、重新抠图或提升 `asset_scale_factor` 后重出资源。

### Figma 可编辑图层导入

Figma 输出不是把整页截图导入成一张图。正确做法是在代码和 QA 完成后，基于同一份 `layers.manifest.json`、完成代码的 computed styles、CSS tokens 和 PNG assets 生成可编辑图层规格。

推荐输出：

```text
figma-code-import/
├── manifest.json
├── code.js
├── FIGMA_IMPORT_REPORT.json
└── README.md
```

图层映射规则：

- Frame：创建 `750 x baseline_height` frame，并保持背景、裁切和层级。
- Text：创建 Figma text node，保留真实文字、字体、字号、行高、字间距、颜色、透明度和位置。
- Simple vector：矩形、圆、线、按钮、卡片、标签、分割线等创建 Figma 原生 shape。
- Bitmap：图标、头像、插画、复杂图表和产品图创建独立 image fill，显示尺寸等于 manifest 的 `css_display_width/height`。
- Reference：可以加入隐藏且锁定的 750px QA render 作为参考层，但它不能替代生产图层。

导入方式优先级：

1. 如果当前环境有 Figma MCP/API/浏览器写入权限，并且用户提供目标 Figma 文件链接，可以直接写入目标文件。
2. 没有直接写入权限时，生成本地 Figma development plugin importer 或 `figma_layer_spec.json`。
3. 不因为缺少 Figma token 或远端权限就放弃；至少交付本地 importer 或 layer spec。

Figma 报告应包含 frame 名称、文本/矢量/PNG 图层数量、替代字体、不可编辑限制、hidden reference layer 状态，以及本地 importer 路径或 Figma 文件链接。

### 验收标准

- 最终生产页面有自适应外层，不能只交付固定 750px 页面。
- 750px 基准画板可用作精确 QA，宽度为 `750px`，高度按源图比例计算。
- 375px 及至少一个其他手机宽度下没有横向滚动，`scrollWidth` 不应明显超过视口宽度。
- 所有关键元素位置、大小、层级和样式可追溯到 manifest。
- PNG 文件真实像素尺寸符合 `asset_scale_factor`，页面显示尺寸符合 `css_display_width/height`。
- 透明 PNG 有 alpha 通道，无白底、灰底、页面底色矩形和明显脏边。
- 文本保持可编辑；简单图形使用代码或 Figma 原生 shape；复杂图形使用独立 PNG。
- 如果导出 Figma，文本节点、shape、image fill 和 z-index 顺序都应与 manifest 一致。

## English Guide

### Project Purpose

This repository packages a Codex skill for strict image-to-code reconstruction. The final deliverable is not merely a fixed 750px page. The expected production output is an adaptive implementation backed by a locked 750px QA baseline, high-density sliced assets, and optional editable Figma layer export.

Primary outputs:

- Adaptive frontend code with a 750px locked artboard scaled by an outer fit wrapper.
- Independent transparent PNG assets exported at 2x, 3x, or 4x density while keeping CSS display sizes fixed.
- `layers.manifest.json` as the source of truth for layout, slicing, QA, and Figma export.
- bbox previews, PNG transparency audits, mobile screenshots, and image comparison QA.
- Optional Figma layer spec or local importer that creates editable text, shapes, and image fills.

### Installation

Place the repository directory in your Codex skills folder:

```text
~/.codex/skills/image-to-code
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

The helper scripts use Pillow and NumPy.

### How to Use It

Trigger the skill explicitly:

```text
Use $image-to-code to convert the selected UI image into adaptive code and transparent PNG assets.
```

Natural-language example:

```text
Convert this mobile UI screenshot into responsive HTML/CSS, export the icons and illustrations as 2x/3x transparent PNGs, and keep the output ready for a later Figma import.
```

### 750px Baseline vs Adaptive Output

The `750px` canvas is the measurement and QA coordinate system:

```text
scale = 750 / source_width
baseline_width = 750
baseline_height = round(source_height * scale)
```

All layer coordinates, sizes, radii, strokes, shadows, gradients, and typography measurements use the same scale. The production page then wraps this locked artboard in a fit layer:

- The `.artboard` stays `width: 750px`.
- Children keep manifest coordinates and do not reflow.
- The outer wrapper computes `scale = min(1, availableWidth / 750)`.
- The wrapper's occupied width and height scale with the visual output.
- Mobile QA should include 375px and at least one other common width.

### Workflow

1. Inspect the source image, framework, output needs, editable text, bitmap layers, responsive constraints, and Figma requirements.
2. Normalize the source to a 750px baseline canvas.
3. Create `layers.manifest.json` before coding.
4. Preview bbox overlays on the source image.
5. Export high-density transparent PNG assets at 2x/3x/4x.
6. Build the locked 750px artboard using manifest coordinates.
7. Add the adaptive fit wrapper.
8. QA text, vector/shape, and bitmap/icon layers separately.
9. Capture and compare the 750px render, then verify 375px and another mobile width.
10. If requested, generate an editable Figma layer spec or local importer from the same manifest/code/assets.

### High-Density PNG Slicing

The PNG file resolution can be higher than the on-page display size:

- Use `asset_scale_factor: 2` by default.
- Use `3` or `4` for small icons, compressed sources, blurry results, or difficult background removal.
- `asset_pixel_width = css_display_width * asset_scale_factor`.
- `asset_pixel_height = css_display_height * asset_scale_factor`.
- CSS display dimensions remain equal to the manifest layer bbox.
- Do not trim the PNG after background removal.
- Keep transparent padding, antialiasing, shadows, and semi-transparent edges.

Example:

```bash
scripts/extract_png_asset.py source.png assets/icons/icon-home-01.png \
  --x 120 --y 88 --width 32 --height 32 \
  --scale-factor 3 \
  --css-width 32 --css-height 32 \
  --remove-bg floodfill \
  --manifest layers.manifest.json \
  --id icon-home-01
```

Audit assets:

```bash
scripts/audit_png_assets.py assets/icons assets/illustrations assets/images \
  --require-transparent-bg \
  --manifest layers.manifest.json
```

### Figma Editable Export

Figma output should be created from `layers.manifest.json`, computed styles, CSS tokens, and PNG assets. Do not import the final page as a single screenshot.

Recommended local output:

```text
figma-code-import/
├── manifest.json
├── code.js
├── FIGMA_IMPORT_REPORT.json
└── README.md
```

Layer mapping:

- Frame: `750 x baseline_height`.
- Text: editable Figma text nodes.
- Simple vectors: native Figma rectangles, ellipses, lines, buttons, dividers, and cards.
- Bitmaps: independent image fills displayed at `css_display_width/height`.
- Reference: optional hidden locked 750px render for QA only.

If Figma API/MCP/browser write access is available and the user provides a target file, the same layer spec can be written directly. Otherwise, the skill should still deliver a local Figma importer or `figma_layer_spec.json`.

### Acceptance Criteria

- The production output includes responsive scaling, not only a fixed 750px page.
- The 750px baseline remains available for exact QA.
- 375px and at least one other mobile width render without horizontal overflow.
- Layer coordinates, dimensions, stacking, and styles trace back to the manifest.
- PNG real pixel sizes match `asset_scale_factor`; CSS display sizes match the layer bbox.
- Transparent PNGs have alpha, clean edges, no white/gray/page-background rectangle, and no clipping.
- Figma exports use editable text nodes, native shapes where possible, independent image fills, and correct z-index order.

## Repository Structure

```text
image-to-code/
├── SKILL.md
├── README.md
├── LICENSE
├── requirements.txt
├── agents/
│   └── openai.yaml
├── references/
│   ├── figma-editable-export.md
│   └── slicing.md
└── scripts/
    ├── audit_png_assets.py
    ├── compare_images.py
    ├── extract_png_asset.py
    └── preview_bboxes.py
```

Key files:

- `SKILL.md`: the full workflow Codex loads when this skill is triggered.
- `references/slicing.md`: detailed bbox, high-density PNG, transparency, and anti-clipping rules.
- `references/figma-editable-export.md`: Figma layer spec and importer guidance.
- `scripts/preview_bboxes.py`: draws bbox overlays on the source image.
- `scripts/extract_png_asset.py`: exports exact-bbox PNG assets at 2x/3x/4x density.
- `scripts/audit_png_assets.py`: audits PNG alpha, transparent backgrounds, edge clipping, and manifest dimensions.
- `scripts/compare_images.py`: compares a rendered screenshot with the reference.

## 鸣谢

学AI, 上L站！[LINUX DO](https://linux.do/)

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
