# Image to Code

`image-to-code` is a Codex skill for turning a selected UI image, screenshot, or exported design into code with pixel-level discipline. It normalizes the source to a fixed `750px` design canvas, exports independent high-density transparent PNG assets, and uses a manifest-driven workflow so every layer can be audited.

`image-to-code` 是一个用于 Codex 的图片转代码与高清切图 skill。它会把用户选中的 UI 图片、截图或设计导出稿按 `750px` 画板宽度进行像素级还原，导出独立高清透明 PNG 资源，并通过 manifest 驱动整个实现与验收流程。

## Contents

- [中文说明](#中文说明)
- [English Guide](#english-guide)
- [Repository Structure](#repository-structure)
- [License](#license)

## 中文说明

### 项目定位

这个项目不是普通的前端模板，也不是自动重新设计工具。它是一套 Codex skill 工作流，用来约束 AI agent 在执行“图片转代码”任务时严格尊重原图：

- 原图是唯一视觉合同。
- 基准画板宽度固定为 `750px`。
- 所有坐标、尺寸、圆角、描边、阴影和字体都使用同一个缩放比例。
- 文本尽量保持为可编辑文本。
- 图标、头像、插画、复杂装饰和产品图从当前源图中切出独立 PNG。
- 简单矩形、按钮、分割线、卡片背景等用代码或原生矢量实现。
- 先做 manifest 和切图，再写页面代码。
- 交付前必须做 bbox 预览、PNG 透明度审计和截图差异对比。

### 安装方式

把整个目录放到 Codex 的 skills 目录中：

```text
~/.codex/skills/image-to-code
```

安装脚本依赖：

```bash
python3 -m pip install -r requirements.txt
```

当前脚本依赖：

- Pillow
- NumPy

### 如何触发

在 Codex 中可以直接点名 skill：

```text
使用 $image-to-code 将当前选中的 UI 图片转换为代码，并导出透明 PNG 切图资源。
```

也可以用自然语言描述任务，例如：

```text
把这张 750px 移动端设计图还原成 HTML/CSS，并把图标和插画单独切成透明 PNG。
```

### 标准工作流程

1. **检查输入图**

   确认源图尺寸、宽高比、目标技术栈、是否需要切图、哪些文字要保留为可编辑文本，以及最终页面需要在哪些宽度下展示。

2. **归一化到 750px 画板**

   以源图宽度为基准计算缩放比例：

   ```text
   scale = 750 / source_width
   final_width = 750
   final_height = round(source_height * scale)
   ```

   所有图层都必须使用同一个 `scale`，不能为了布局更顺眼单独调整元素。

3. **建立 `layers.manifest.json`**

   manifest 是布局和切图的唯一数据源。每个图层至少记录：

   - `id`
   - `type`
   - `source_bbox`
   - `scaled_bbox`
   - `z_index`
   - `asset`
   - `asset_scale_factor`
   - `css_display_width`
   - `css_display_height`
   - `transparent_required`

4. **预览 bbox**

   在源图上画出 manifest 中的 bbox，确认切图框没有裁掉主体，也没有误带相邻元素。

   ```bash
   scripts/preview_bboxes.py source.png layers.manifest.json qa/bbox-preview.png --only-type bitmap
   ```

5. **导出高清 PNG 资源**

   使用精确 bbox 从源图导出 PNG。高清导出只提高 PNG 文件真实像素，不改变它在页面中的 CSS 显示尺寸。

   ```bash
   scripts/extract_png_asset.py source.png assets/icons/icon-user.png \
     --x 120 --y 980 --width 72 --height 72 \
     --scale-factor 3 \
     --remove-bg floodfill \
     --manifest layers.manifest.json \
     --id icon-user
   ```

6. **实现 750px 固定画板**

   页面根画板固定为 `width: 750px`。关键元素用 manifest 坐标定位。响应式只允许在外层整体缩放画板，不应该对子元素重新排版。

7. **审计 PNG 资源**

   检查 PNG 是否带 alpha 通道、背景是否透明、是否贴边，以及尺寸是否和 manifest 匹配。

   ```bash
   scripts/audit_png_assets.py assets/icons assets/images \
     --require-transparent-bg \
     --manifest layers.manifest.json
   ```

8. **截图对比验收**

   将最终渲染截图与 750px 参考图做差异对比。

   ```bash
   scripts/compare_images.py reference-750.png render-750.png --json
   ```

### Manifest 示例

```json
[
  {
    "id": "avatar",
    "type": "bitmap",
    "source_bbox": { "x": 86, "y": 112, "width": 120, "height": 120 },
    "scaled_bbox": { "x": 86, "y": 112, "width": 120, "height": 120 },
    "z_index": 10,
    "asset": "assets/images/avatar.png",
    "asset_pixel_width": 360,
    "asset_pixel_height": 360,
    "asset_scale_factor": 3,
    "css_display_width": 120,
    "css_display_height": 120,
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

### 交付物

一次完整的图片转代码任务通常应该交付：

- 还原后的前端代码
- 独立透明 PNG 切图资源
- `layers.manifest.json`
- bbox 预览图
- 750px 基准截图
- 至少一个移动端自适应截图
- 简短还原报告，说明资源、误差、限制和验收结果

### 验收标准

- 750px 基准画板宽度精确为 `750px`。
- 画板高度按源图比例计算，不人为优化。
- 所有主要图层位置、大小、层级和样式可追溯到 manifest。
- 文本为可编辑文本，除非它属于复杂位图的一部分。
- 图标、头像、插画和复杂装饰来自当前源图切图。
- PNG 资源透明、高清、不贴边、不带白底或灰底。
- bbox 预览与源图元素边界一致。
- 最终截图和参考图无明显错位、缺图、裁切或替代素材。

## English Guide

### What This Project Is

This repository packages a Codex skill for strict image-to-code reconstruction. It is designed for UI screenshots, mobile app screens, Figma exports, web mockups, posters, and similar design images where the source image is the visual contract.

The skill pushes Codex to follow a measured process instead of improvising a new layout:

- Normalize the source image to a `750px`-wide design canvas.
- Keep one global scale for every coordinate and visual property.
- Build a `layers.manifest.json` before coding.
- Export bitmap/icon layers from the current source image.
- Keep text editable whenever possible.
- Recreate simple shapes with code.
- Audit exported assets and compare the final render against the reference.

### Installation

Place the repository directory in your Codex skills folder:

```text
~/.codex/skills/image-to-code
```

Install script dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Dependencies:

- Pillow
- NumPy

### How to Use It

Trigger the skill explicitly in Codex:

```text
Use $image-to-code to convert the selected UI image into code and export transparent PNG assets.
```

You can also describe the task naturally:

```text
Convert this mobile UI screenshot into HTML/CSS at a 750px design width, and export the icons and illustrations as separate transparent PNG files.
```

### Step-by-Step Workflow

1. **Inspect the source**

   Record the original image dimensions, target output type, required editable text, bitmap layers, responsive constraints, and project framework.

2. **Normalize to a 750px canvas**

   Calculate the global scale:

   ```text
   scale = 750 / source_width
   final_width = 750
   final_height = round(source_height * scale)
   ```

   Apply this scale to every coordinate, size, border radius, stroke, shadow, gradient position, and text measurement.

3. **Create `layers.manifest.json`**

   The manifest is the source of truth for layout and slicing. Each layer should record its source bbox, scaled bbox, type, z-index, asset path, and transparency requirements.

4. **Preview bounding boxes**

   Draw bbox overlays on the original source image before exporting assets:

   ```bash
   scripts/preview_bboxes.py source.png layers.manifest.json qa/bbox-preview.png --only-type bitmap
   ```

5. **Export high-density PNG assets**

   Export bitmap/icon layers from the exact bbox. Increasing `--scale-factor` improves file resolution while the CSS display size remains unchanged.

   ```bash
   scripts/extract_png_asset.py source.png assets/icons/icon-user.png \
     --x 120 --y 980 --width 72 --height 72 \
     --scale-factor 3 \
     --remove-bg floodfill \
     --manifest layers.manifest.json \
     --id icon-user
   ```

6. **Build the 750px fixed canvas**

   Implement the base canvas as `width: 750px`. Position key layers from the manifest. Responsive behavior should wrap and scale the whole canvas, not reflow individual children.

7. **Audit exported PNGs**

   Check alpha, transparent backgrounds, edge clipping, and manifest dimensions:

   ```bash
   scripts/audit_png_assets.py assets/icons assets/images \
     --require-transparent-bg \
     --manifest layers.manifest.json
   ```

8. **Compare the final render**

   Compare the rendered screenshot with the 750px reference image:

   ```bash
   scripts/compare_images.py reference-750.png render-750.png --json
   ```

### Expected Deliverables

A complete image-to-code run should usually include:

- The generated frontend code
- Independent transparent PNG assets
- `layers.manifest.json`
- bbox preview image
- 750px baseline screenshot
- at least one responsive mobile screenshot
- a short restoration report covering assets, known limits, and QA results

### Acceptance Criteria

- The baseline canvas is exactly `750px` wide.
- Canvas height follows the source aspect ratio.
- Main layer coordinates, dimensions, stacking, and styles trace back to the manifest.
- Text stays editable where practical.
- Icons, avatars, illustrations, and complex decorations are sliced from the current source image.
- PNG assets are transparent, high-density, unclipped, and free from white/gray rectangular backgrounds.
- bbox previews align with the source image.
- Final screenshot comparison shows no obvious shifts, missing assets, clipping, or substitute graphics.

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

- `SKILL.md`: the instructions Codex loads when this skill is triggered.
- `agents/openai.yaml`: UI metadata for the skill list.
- `references/slicing.md`: detailed rules for bbox measurement, PNG export, and transparency.
- `references/figma-editable-export.md`: guidance for turning the manifest/code/assets into editable Figma layer specs.
- `scripts/preview_bboxes.py`: draws source bboxes for review.
- `scripts/extract_png_asset.py`: exports exact-bbox PNG assets.
- `scripts/audit_png_assets.py`: audits transparent PNG outputs.
- `scripts/compare_images.py`: compares the final render against a reference.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
