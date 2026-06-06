# Figma 可编辑导出思路

当用户要求“导入 Figma”“可编辑图层”“复制到 Figma”“给我 Figma 版本”时使用本参考。

核心原则：不要把最终网页或 750px QA 截图当成单张图片导入。把完成稿拆成 Figma 能创建的真实图层：文本节点、矩形/椭圆/线条/矢量节点、图片填充节点和必要的隐藏参考图层。

采用将网页图层映射为 Figma 图层的通用思路，但不要依赖某个特定本地插件：从已完成的 code、computed styles、`layers.manifest.json` 和 PNG assets 生成 Figma 图层数据，再用当前环境可用的方式导入。

## 输入

- `layers.manifest.json`：坐标、尺寸、z-index、图层类型、资源路径、透明要求。
- 完成后的 750px 页面代码：文本内容、CSS token、渐变、阴影、圆角、描边、透明度。
- PNG assets：独立图标、插画、头像、产品图。
- QA render：只作为隐藏 locked reference layer，不作为生产图层。

如果 manifest 缺少 Figma 所需样式，必须补充或生成 `figma_layer_spec.json`。不要从整页截图重新猜图层。

## 推荐输出

生成一个独立的 `figma-importer/` 或 `figma-code-import/` 文件夹：

```text
figma-code-import/
├── manifest.json
├── code.js
├── FIGMA_IMPORT_REPORT.json
└── README.md
```

`code.js` 应嵌入或读取图层规格和 PNG assets，并在 Figma 插件运行时创建 frame 和子图层。若本地文件读取不可用，把 assets base64 嵌入 `code.js`。

## 图层映射

- Frame：创建 `750 x final_height` frame，`clipsContent = true`，背景用 Figma 原生 fill/gradient。
- Text：创建 `figma.createText()`，写入真实文字、fontName、fontSize、lineHeight、letterSpacing、fills、opacity、alignment、x/y/width/height。文本必须可编辑。
- Simple vector：矩形、圆、线、分割线、按钮、卡片、标签、简单背景用 Figma 原生 shape，写入 fill、stroke、cornerRadius、effects。
- Bitmap：图标、插画、头像、复杂图表创建 rectangle image fill；显示尺寸必须等于 manifest 的 `css_display_width/height`，不能按 PNG 文件像素撑大。
- Complex effects：无法可靠转成 Figma 属性时，使用独立 PNG 图层，并在报告中标为不可编辑限制。
- Reference：可以加入隐藏且锁定的 `locked-reference-render-750-hidden`，用于 QA，不计入生产可编辑层。

## 导入方式选择

优先顺序：

1. 当前环境有 Figma MCP/API/浏览器权限：用同一份 layer spec 直接创建或提交到目标 Figma 文件。
2. 没有直接写入权限：生成本地 Figma development plugin importer，让用户在 Figma 里运行。
3. 环境支持 Figma HTML clipboard：把 DOM/CSS/assets 编码成 Figma 可识别的 clipboard payload；失败时回退到本地 importer。

不要因为没有 Figma 写入 token、MCP 或浏览器权限就说“导入不了”。在缺少权限时仍必须交付可运行的本地 importer 或明确列出缺少哪项权限。

## QA

导入后检查：

- Frame 尺寸等于 `750 x final_height`。
- 图层数量和 manifest 类型统计一致。
- z-index 顺序正确。
- 文本图层可编辑，不是图片。
- 矢量图层是 Figma shape，不是截图。
- PNG 图层清晰，透明边缘在 Figma 中没有白/灰矩形底。
- 隐藏参考图层存在但 locked/hidden，不遮挡生产层。

报告必须包含：目标 Figma 文件或本地 importer 路径、frame 名称、文本/矢量/PNG 图层数量、替代字体、不可编辑限制、是否有 hidden reference layer。
