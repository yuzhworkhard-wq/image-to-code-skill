---
name: image-to-code
description: 像素级 750px 图片转代码与高清切图工作流。当 Codex 需要把当前选中的 UI 图片、截图、App/Web 设计稿、Figma 图片导出稿或设计长图转换为代码，并输出独立透明 PNG 切图资源时使用。适用于严格 1:1 等比例还原、画板宽度精确 750px、高清放大切图、防模糊和背景抠除、必要时用 image2/imagegen 抠透明 PNG、文本可编辑、简单图形原生矢量/代码化，最终代码需要自适应适配，或需要把完成稿导出/导入 Figma 为可编辑图层的任务。
---

# Image To Code

## 目标

把用户提供或当前选中的 UI 图片还原为代码，并导出必要的独立高清切图资源。

原图就是视觉合同。不要把它重新设计成“更合理”的界面，不要做排版优化，不要主观调整间距。必须先按 750px 宽度等比归一化，再按原图元素的位置、比例、层级、颜色、透明度和样式进行还原。

750px 是设计基准坐标，不是最终页面的唯一显示宽度。生产代码必须在保持 750px 基准稿不变的前提下提供自适应缩放；切图资源必须有足够像素密度，不能因为源 bbox 小而在页面里发糊。高清切图只提高 PNG 文件真实像素，不改变它在页面里的位置和显示大小。

## 最高优先级规则

当用户要求“严格等比例缩放至画板宽度精确 750px”时，这条规则高于所有常规前端、设计和响应式建议。

- 整体画板宽度必须精确为 `750px`。
- 画板高度必须根据原图宽高比自动计算，不能人为设定或优化。
- 所有元素必须使用同一个全局缩放比例。
- 保持所有元素的相对位置、相对大小、层级关系、堆叠顺序、颜色、透明度、阴影、渐变、圆角、描边和样式属性。
- 禁止自动调整任何元素的位置、大小、对齐、间距、排版或视觉层级。
- 禁止重新设计、优化布局、合并独立元素、拉伸素材、改变颜色或简化效果。
- 禁止把图标或位图强行转换为矢量路径。
- 禁止使用相似图标库、相似插画、AI 生成图、CSS 临摹图或占位素材替代原图中的图标/位图。
- 禁止自动创建 Figma/export 的 Slice 对象。只有在需要切图资源时，才按元素边界导出独立 PNG 文件。
- 如果代码优雅性和视觉还原发生冲突，视觉还原优先。
- 750px 基准稿必须可精确复核；生产页面必须同时提供按容器/视口等比缩放的自适应版本。

## 跨目录调用一致性

无论用户在哪个项目文件夹调用本 skill，都必须只以本次用户提供/选中的原图为视觉源。不要沿用其他会话、其他文件夹、旧示例或历史任务里的结构、素材、配色、页面区域和实现假设。

- 每次调用都必须重新读取当前源图尺寸。
- 每次调用都必须重新测量当前源图元素坐标。
- 每次调用都必须重新建立当前源图的图层分类表。
- 不得复用旧项目里的图标、插画、头像、卡片素材或布局参数，除非用户明确指定这些就是源素材。
- 不得因为当前项目已有组件或 CSS，就把原图自动改造成项目现有组件样式。
- 如果没有源图局部切图能力，宁可保留完整局部裁片作为临时素材并说明限制，也不要用“看起来差不多”的替代图重画。

## 执行流程

1. 检查输入图片和项目约束。
2. 把原图等比归一化到 750px 宽度。
3. 建立 `layers.manifest.json`：记录每个图层的原图 bbox、缩放后 bbox、类型、z-index、导出文件名。
4. 为每个 bitmap/icon 资源确定 `asset_scale_factor`，默认 `2`，小图标、低分辨率源图或抠边脏时用 `3` 或 `4`。
5. 先按 manifest 导出高清切图资源，再写代码。禁止先凭感觉写代码再补切图。
6. 对所有 icon/illustration/复杂位图默认要求透明 PNG；本地背景抠除不干净、审计失败或棋盘格/黑底/白底预览仍有脏底时，必须使用 image2/imagegen 做透明 PNG 背景抠除兜底，并保持页面显示外框、构图和主体位置不变。
7. 在 750px 基准画板中使用 manifest 的精确坐标实现代码。
8. 完成 750px 基准代码后，进入自适应细化阶段：加外层 fit wrapper，按容器或视口整体缩放 750px 画板，不得对子元素重新排版。
9. 分模块校验：矢量、文本、位图/图标切图分别验收。
10. 做整页 750px 叠图复核，并做 375px 手机宽度和至少一个其他手机宽度的自适应截图。
11. 根据具体错位、缺图、裁切、样式差异或手机端溢出继续迭代。
12. 交付代码、高清切图资源、manifest 和简短还原报告。
13. 代码和 QA 完成后，若用户要求 Figma 或需要继续交付，按同一份 manifest/code/assets 导出可编辑 Figma 图层规格或本地 Figma importer；只有需要直接写入远端 Figma 文件时，才索取 Figma 链接和写入权限。

## 输入检查

开始前先确认：

- 原图尺寸和宽高比
- 目标类型：网页、移动端界面、组件、海报、邮件、游戏 UI 或静态 HTML
- 是否已有项目框架和技术栈
- 是否要求只输出代码、只输出切图，还是代码加切图
- 哪些文字必须变成可编辑文本
- 哪些复杂图形需要保留为透明 PNG
- 是否有明确的响应式断点、最大宽度、嵌入容器或移动端/桌面端展示要求

如果仓库已有框架，遵循现有框架。没有项目时，静态页面优先使用 HTML/CSS/JS；只有在组件结构或交互确实需要时才使用 React/Vite。

## 750px 等比归一化

假设原图尺寸为 `source_width x source_height`：

```text
scale = 750 / source_width
final_width = 750
final_height = round(source_height * scale)
scaled_x = original_x * scale
scaled_y = original_y * scale
scaled_width = original_width * scale
scaled_height = original_height * scale
```

同一个 `scale` 必须应用到：

- 所有坐标
- 所有宽高
- 所有圆角
- 所有描边
- 所有阴影偏移和模糊
- 所有渐变位置
- 所有图标和位图外框
- 所有文字字号、行高和字间距

主交付物是锁定的 750px 定稿画板。响应式规则不能影响 750px 版本的坐标、比例和叠图复核。最终代码必须在 750px 基准外再提供自适应缩放层。

## 强制 Manifest

任何图片转代码 + 切图任务都必须先创建 manifest。manifest 是布局和切图的唯一数据源，不允许在代码里重新估算位置。

每个图层至少记录：

```json
{
  "id": "card-wallet-illustration",
  "type": "bitmap",
  "source_bbox": { "x": 338, "y": 520, "width": 116, "height": 122 },
  "scaled_bbox": { "x": 338, "y": 520, "width": 116, "height": 122 },
  "z_index": 24,
  "asset": "assets/illustrations/card-wallet-illustration.png",
  "asset_pixel_width": 232,
  "asset_pixel_height": 244,
  "asset_scale_factor": 2,
  "css_display_width": 116,
  "css_display_height": 122,
  "transparent_required": true,
  "notes": "从当前源图裁切，保持原图露出比例"
}
```

规则：

- `source_bbox` 必须来自当前源图测量，不得凭布局推算。
- `scaled_bbox` 必须由同一个 `scale` 计算得到。
- bitmap/icon 的 `asset_pixel_width/height` 可以高于 `scaled_bbox.width/height`，但代码里的 `css_display_width/height` 必须等于 `scaled_bbox` 尺寸。也就是文件分辨率 2x/3x，页面占位仍是原元素外框大小。
- `asset_scale_factor = asset_pixel_width / css_display_width`。默认至少 `2`；小于 `64px` 的图标、源图压缩明显、边缘脏或放入页面后发糊时使用 `3` 或 `4`。
- 代码中的每个图片层、文本层、矢量层都必须能追溯到 manifest。
- 如果实现截图和原图不一致，先修 manifest 坐标，再修代码。
- 没有 manifest 的交付视为未完成。
- `assets/icons/`、`assets/illustrations/`、卡片插画、导航图标、按钮图标、状态图标和不规则装饰图默认 `transparent_required: true`。不得因为抠图困难、背景和卡片颜色接近、或本地脚本抠除失败就把它改成 `false`。
- 只有照片、真实产品图、截图、纹理背景、完整矩形 banner 或背景本身就是视觉内容的位图，才允许 `transparent_required: false`，并必须在 `notes` 里说明为什么保留矩形背景。
- 如果某个 PNG 的四角 alpha 不为 0、棋盘格上出现白/灰/页面底色矩形、或 `audit_png_assets.py --require-transparent-bg` 失败，manifest 必须保持 `transparent_required: true`，并重出资源；不能通过改 manifest 跳过验收。

## Bbox 测量和预览

切图区域不能凭感觉。每个需要导出的资源必须先完成 bbox 预览校验，再导出 PNG。

流程：

1. 在原图原始尺寸上测量 `source_bbox`，不要在浏览器缩放预览图上估算。
2. bbox 必须覆盖完整元素外框，包括透明留白、浅色底形、阴影、半透明边缘和被遮挡但可见的外缘。
3. 对边界不确定的资源，建立 2-3 个候选 bbox，选择能完整覆盖且不多带相邻元素的最大安全框。
4. 使用 `scripts/preview_bboxes.py` 或等效方式，把 manifest 中的 bbox 画到源图上生成预览图。
5. 只有当预览框与原图元素完整外框对齐后，才允许切图。
6. 如果预览框框到了相邻文字、相邻图标、卡片背景大块区域，必须修 bbox。
7. 如果导出后发现缺失、贴边、白底、灰底，必须回到 bbox 预览步骤重测，不能只在 PNG 上修补。
8. 如果源图 bbox 很小，预览通过后仍必须高清导出；不要把低像素裁片直接当生产素材。

交付报告必须包含 bbox 预览图路径或说明已做等效原图框选复核。

## 图层分类规则

实现前必须把每个可见元素归类：

- **文本图层**：全部还原为可编辑文本或代码文本。匹配文字内容、字体、字号、字重、行高、字间距、颜色、透明度、对齐方式、换行和精确坐标。
- **简单矢量/规则图形**：矩形、圆形、线条、边框、按钮背景、分割线、简单渐变和简单阴影，转为 CSS/Figma 原生形状或代码。
- **位图/图标切图**：按钮图标、导航图标、功能图标、状态图标、头像、产品图、卡片插画、装饰图、背景素材、不规则复杂图形，全部从当前源图中提取为独立透明 PNG。不得用相似图标、相似插画、CSS 临摹、emoji、字体图标或生成图替代。
- **复杂图表/可视化**：复杂图形整体保留为透明 PNG 图层；图表中的可读文字单独提取为可编辑文本，覆盖在对应位置。

每个独立图标和位图都必须保持独立图层和独立文件。不得合并、编组导出或做成 sprite，除非用户明确要求。

## 视觉规格提取

编码前先为自己写一份简短视觉提取记录：

- 画板尺寸、缩放比例和最终高度
- 页面网格、主要区域、对齐边缘和层级顺序
- 外边距、模块间距、卡片内边距和重复节奏
- 字体、字号、字重、行高、字间距、大小写
- 背景色、文字色、边框色、强调色、阴影色、渐变色
- 图片、图标、插画和背景素材的裁切方式
- 阴影、模糊、透明度、混合模式、圆角和描边

尽量使用测量工具、截图、图像采样和浏览器计算样式，不要只靠目测。无法获得原字体时，选择最接近的可用字体，并通过字号、字重、行高和间距微调到视觉一致。

## 布局锁定规则

布局不允许使用自动流式排版来“复刻大概结构”。必须用 750px 画板坐标系锁定。

- 根画板必须是 `width: 750px`，高度等于归一化高度。
- 画板内所有关键层必须使用 manifest 坐标定位。
- 页面预览时可以整体缩放画板，但不能对子元素重新排版。
- 禁止使用 flex/grid 的自动分布结果替代原图坐标；flex/grid 只能在数值完全等于 manifest 坐标时作为实现手段。
- 顶部头像区、数据区、会员条、四宫格卡片、更多服务、底部导航必须分别和原图同 x/y/width/height。
- 如果截图里出现内容整体上移、下移、卡片变宽、间距变大、头像被裁、底部导航位置变化，直接判定布局失败。

## 切图计划

不要把整张设计稿切成一张大图，除非用户明确要求静态位图。文字、按钮、卡片、边框、分割线等应尽量用代码实现。但复杂插画、头像和图标必须从当前源图裁切，不能重绘。

必须导出独立透明 PNG 的内容：

- 所有图标
- 头像、logo、状态栏图标、底部导航图标
- 产品图、截图、照片
- 卡片内的钱包、礼物、徽章、星星、勾选章、装饰块等复杂插画和不规则装饰图
- 复杂图表、数据可视化和手绘元素
- 纹理、遮罩、复杂阴影或无法稳定用 CSS 复现的图形
- 无法从现有图标库准确还原的 logo 或品牌标识

不要为这些内容导出切图：

- 普通文字
- 简单按钮、卡片、边框、分割线、标签、输入框
- 简单 CSS 渐变、阴影、圆角矩形或网格背景
- 只有在与原图形状、比例、线宽、端点、圆角和视觉重量完全一致时，才允许用项目现有图标系统复现；否则必须从原图提取 PNG。

涉及切图时必须阅读 `references/slicing.md`，按其中的命名、格式、透明背景和禁止裁边规则执行。

优先使用或等效执行 `scripts/extract_png_asset.py` 从源图按 bbox 导出高清 PNG。该脚本不会自动 trim，输出 PNG 文件像素画布等于 `bbox * asset_scale_factor`，页面显示外框仍等于 `scaled_bbox`，可在高清像素画布内移除纯色背景并保留 alpha。

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

导出规则：

- 默认 `--scale-factor 2`；小图标、低分辨率源图、边缘脏或放入页面后发糊时用 `3` 或 `4`。
- 背景抠除必须发生在高清像素画布里，不能先把低清图抠干净失败后再直接放大。
- manifest 必须记录 PNG 文件真实像素尺寸和 CSS 显示尺寸；代码显示尺寸必须等于 `scaled_bbox`，不能因为 PNG 是 2x/3x 就把页面位置撑大。

导出前必须先用 `scripts/preview_bboxes.py` 检查 bbox 区域。没有 bbox 预览校验的切图结果不可信。

## 禁止近似重绘

下列行为全部视为失败，即使页面看起来“更规整”或“更清晰”：

- 把原图的小图标换成 lucide、Material Icons、SF Symbols 或其他相似图标。
- 把原图卡片里的钱包、礼盒、徽章、星星、人物头像、状态栏图标重新画成另一套风格。
- 把原图中靠左/靠右/局部露出的插画改成居中、放大、缩小或重新裁切。
- 把四宫格、服务宫格、会员条、底部导航重新排版成更均匀的布局。
- 为了适配代码组件，把原图卡片高度、圆角、间距、文字位置、图片比例改掉。
- 把原图的小装饰图放大成主视觉，或把原图的大图缩小成装饰。
- 用渐变、阴影或 CSS 图形模拟复杂位图，导致形状和原图不一致。

如果无法精准矢量化或代码化某个复杂元素，必须把该元素从源图按完整外框提取为 PNG，而不是近似重绘。

## 透明背景硬规则

凡是 manifest 中 `transparent_required: true` 的资源，最终 PNG 必须有 alpha 通道，并且目标背景必须透明。

- 图标、按钮符号、导航符号、卡片插画、金币/礼物/钱包/人物/装饰图等不规则资源默认都属于 `transparent_required: true`，即使它们原来放在彩色卡片、渐变区或浅色底上。
- PNG 不能带白底、灰底、页面底色或卡片底色，除非该底色是元素本身的一部分。
- 从截图裁切出的白/灰/纯色背景必须抠除，但页面显示画布和构图不能改变；高清 PNG 的文件像素尺寸仍按 `asset_scale_factor` 保留。
- 切图 bbox 必须先覆盖完整元素并额外外扩安全留白，再做背景抠除；不得先抠除再按主体重新裁边。
- 抠除背景后不得 trim，不得重新计算 bbox，不得让主体贴边。
- 本地 `remove-bg corners/floodfill` 或等效抠图仍有白边、灰边、脏底、缺角时，必须使用 image2/imagegen 的图片编辑能力做透明 PNG 背景抠除兜底。
- 使用 image2/imagegen 时必须把当前高清裁片作为编辑目标，只允许移除背景为透明 alpha；禁止重新生成相似图标、相似头像、相似插画或改变主体形状、颜色、比例、角度、阴影、边缘和画布尺寸。
- 交付前必须在棋盘格、黑底、白底上检查透明边缘。只在原页面背景上看不出脏底不算通过。
- 必须运行 `scripts/audit_png_assets.py --require-transparent-bg` 或等效审计检查所有 `transparent_required: true` 的 PNG；如果默认 Python 缺 Pillow/numpy，必须换用可用运行时、安装依赖或用等效脚本重跑，不能跳过。
- 审计中出现 `transparent_bg_ok=false`、`corner_alpha_max` 高于阈值、`has_alpha_channel=false`、或 `touches_edge` 未解释清楚时，必须重出 PNG。典型失败是插画文件四角 alpha 为 255，说明仍带完整矩形背景。
- 如果无法可靠抠除背景，必须说明并保留完整局部裁片作为临时失败态，不能谎称透明切图完成。

## 防裁切硬规则

切图宁可画布偏大并保留透明留白，也绝不能裁掉任何一段内容。任何“只截到一段”“边缘缺一块”“阴影/浅色底被削掉”“图标贴边”的结果都判定为失败。

- 切图边界必须来自原图中该元素的完整视觉外框，而不是来自抠图后的深色主体外框。
- 图标包含浅色圆形/八边形底、阴影、光晕、渐变底时，底形属于完整视觉范围，不能被忽略。
- 如果图标主体和浅色底需要拆层，浅色底必须用代码/矢量单独复现，图标 PNG 仍必须保留完整主体和必要透明留白。
- 如果无法稳定判断真实边界，必须向四周扩展安全留白，默认至少 `4px-12px`，而不是缩小裁切框。
- 导出的 PNG 中，任何非透明像素触碰画布四边都必须判定为疑似裁切，必须扩大画布重出。
- 有阴影、模糊、发光、抗锯齿边缘的资源，必须保留完整半透明像素，不能只保留不透明主体。
- 服务宫格、底部导航、功能入口这类图标，必须逐个图标整件导出，不能从图标中间截取局部，也不能只截一个角、一条边或一个内部符号。
- 切图尺寸校验不只看视觉是否像，还必须检查页面显示尺寸是否覆盖原元素完整外框、PNG 文件像素尺寸是否符合 `asset_scale_factor`。

## 自适应细化硬规则

750px 基准画板写完后，必须单独做一轮手机端适配；没有 375px 验证的交付视为未完成。

- 750px 坐标系保持锁定：`.artboard` 或等效根画板仍是 `width: 750px`，高度仍是归一化高度。
- 自适应只发生在外层：`scale = min(1, availableWidth / 750)`，其中 `availableWidth` 是容器宽度或视口宽度。
- 手机 App/移动端界面默认全宽适配：在 `320px-430px` 视口内默认 `availableWidth = 100vw`，不要自动减 `16px/32px` 外边距；只有原图本身有外部留白、用户要求嵌入容器，或网页场景需要页面 gutter 时才加 gutter。
- 外层占位尺寸必须同步缩放：wrapper 的实际宽高应等于 `750 * scale` 和 `final_height * scale`，不能让未缩放的 750px 画板撑开页面。
- 禁止用 `min-width: 750px`、固定 `body` 宽度、横向滚动、浏览器缩放、截图缩放或只改 `zoom` 来冒充手机端适配。
- 禁止为了适配 375px 重新排版子元素、改字号、改间距、改坐标或改图层尺寸；子元素仍追溯 manifest 坐标。
- 如果用户明确要求桌面网页式响应式重排，必须先完成 750px 像素版和整体缩放版，再把重排作为额外版本，并在交付说明中标明偏离原图的位置。
- 375px 全宽演示时，渲染宽度应接近 `375px`，缩放比例应接近 `0.5`；如有 gutter，必须在报告里说明实际可用宽度和比例。

## 代码实现规则

- 首先匹配原图，不做主观优化。
- 在 750px 基准画板中优先使用精确像素坐标和固定尺寸。
- 可以使用绝对定位实现锁定画板，只要更有利于还原。
- 使用 CSS 变量保存提取出的颜色、圆角、间距、字体和阴影 token。
- 保留真实内容层级，不要用说明文字或占位文案替代原内容。
- 不要增加原图不存在的外层卡片、装饰容器或嵌套结构。
- 字间距默认按原图提取；原图没有明显 tracking 时保持 `0`。
- 不要用视口宽度直接缩放字体。
- 交付代码必须有自适应外层，不能只写死 750px。自适应外层只负责整体等比缩放或在更大容器中居中显示，不得对子元素重新排版。

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
  --fit-gutter: 0px;
  --board-scale: min(1, calc((100vw - var(--fit-gutter) * 2) / (var(--board-w) * 1px)));
}

.fit-shell {
  width: 100%;
  display: grid;
  place-items: start center;
  overflow-x: clip;
}

@media (min-width: 751px) {
  .fit-shell {
    --fit-gutter: 24px;
  }
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

如果需要按父容器而不是视口适配，使用 `ResizeObserver` 或项目现有容器测量方式设置 `--board-scale = containerWidth / 750`。无论哪种方式，750px QA 截图时必须让 `--board-scale: 1`。

如果 CSS 除法在目标浏览器或项目构建链中不稳定，使用一小段 JS 设置缩放变量：

```js
const root = document.documentElement;
const fitShell = document.querySelector(".fit-shell");
const fit = () => {
  const availableWidth = fitShell.getBoundingClientRect().width;
  root.style.setProperty("--board-scale", String(Math.min(1, availableWidth / 750)));
};
new ResizeObserver(fit).observe(fitShell);
window.addEventListener("resize", fit);
fit();
```

## Figma 可编辑图层导入

涉及把完成稿导出/导入 Figma 为可编辑图层时，必须阅读 `references/figma-editable-export.md`。这里的“可编辑”指文本是 Figma text node，简单形状是 Figma shape，复杂位图是独立 image fill；禁止把整页截图当作唯一生产图层。

代码完成并通过 750px/手机端 QA 后，如果用户要求 Figma，必须生成可编辑 Figma 导出物。不要在代码实现前打断用户索取 Figma 链接，除非用户一开始就明确要求直接写入某个 Figma 文件。

询问模板：

```text
代码和切图已经完成。我可以继续导出一个可编辑 Figma 图层版本：优先生成本地 Figma importer；如果你要我直接写入某个 Figma 文件，请提供文件链接并确认我有写入权限。
```

执行规则：

1. 使用 `layers.manifest.json`、完成代码的 computed styles、CSS tokens 和 PNG assets 生成 `figma_layer_spec.json` 或等效 layer spec；不要从最终网页截图重新猜图层。
2. 默认生成独立本地 Figma importer（例如 `figma-code-import/manifest.json` + `code.js`），把 manifest、样式和 PNG assets 嵌入或打包进去。这个 importer 不依赖任何特定本地插件或本机路径。
3. 如果当前环境有 Figma MCP/API/token/浏览器权限，并且用户提供目标文件链接，可以用同一份 layer spec 直接写入 Figma。
4. 如果没有直接写入权限，仍必须交付本地 importer 或 layer spec；不得简单回答“导入不了”。
5. 在 Figma 中创建 `750px x final_height` frame，按 `z_index` 从低到高创建图层，并保持每个图层的 `id` 或可读名称。
6. 文本图层创建为 Figma text node；简单矢量/规则图形创建为 Figma shape；位图/图标/头像/复杂插画使用独立高清 PNG image fill，显示尺寸等于 manifest 的 `css_display_width/height`。
7. 可用整页 QA render 作为隐藏且 locked 的 reference layer，但必须标明不是生产图层，不能覆盖真实可编辑层。
8. 导入或生成 importer 后检查 frame 尺寸、图层数量、z-index、文本可编辑性、PNG 清晰度和透明边缘。

Figma 导出报告必须包含：Figma 文件链接或本地 importer 路径、目标页面/frame 名称、导入的文本/矢量/PNG 图层数量、替代字体或不可编辑图层限制、是否有 hidden locked reference layer。

## 验收与复核

只要能渲染浏览器页面，就必须截图验证：

1. 启动本地页面或开发服务器。
2. 截取 750px 画板截图。
3. 与 750px 归一化原图进行叠图对比。
4. 分别校验矢量图层、文本图层、位图/图标切图模块。
5. 将浏览器视口切到 `375px` 宽，截取手机端截图，检查画板是否按比例缩放到可用宽度、没有横向滚动、没有未缩放 750px 内容撑开页面。
6. 再检查至少一个其他手机宽度，优先 `320px`、`390px`、`414px` 或 `430px` 中最接近用户演示设备的尺寸。
7. 先修正最大差异：画板尺寸、层级顺序、坐标、宽高、背景、字体大小、手机端缩放比例和横向溢出，再修细节效果。
8. 重复截图和对比，直到剩余差异都有明确原因。

必须保留一个 QA 对照方式：可以是半透明底图 overlay、单独对比截图、或差异图。最终生产层不能依赖整页底图，但开发验收必须能证明实现层和源图对齐。

可以使用 `scripts/compare_images.py` 做快速图片差异指标检查。像素指标只是辅助判断；字体抗锯齿、系统字体替换和浏览器渲染差异可能导致可接受的少量差异。

切图资源交付前必须运行或等效执行 `scripts/audit_png_assets.py --require-transparent-bg`：检查 PNG 四边是否有非透明像素贴边、是否包含 alpha 透明通道、角落背景是否透明，并在有 manifest 时校验每张 PNG 的真实像素宽高 `asset_pixel_width/height`。任何 `touches_edge`、`transparent_bg_ok=false` 或宽高不一致都必须先修复。若审计脚本因缺 Pillow/numpy 等依赖失败，必须换用可用 Python、安装依赖或写等效审计；依赖失败不能作为跳过透明检查的理由。

还必须检查透明度：透明 PNG 如果 `has_alpha_channel=false`、背景区域 alpha 不为 0、或在棋盘格上出现白/灰色矩形底，判定失败。

## 验收标准

- 整体画板宽度必须精确为 `750px`。
- 在 `375px` 手机视口中，页面不得出现横向滚动；`document.documentElement.scrollWidth` 必须小于等于视口宽度加 `1px` 容差。
- 在 `320px-430px` 常见手机宽度中，fit wrapper 必须按可用宽度等比缩放整张 750px 画板，不能露出未缩放的 750px 固定宽内容。
- 矢量形状的坐标、宽高、圆角、描边、渐变、颜色和透明度必须对齐 750px 原图，主观允许误差为 `0px`。
- 文本内容、坐标、字号、字重、行高、字间距、颜色、对齐方式和换行必须对齐原图。
- 每个图标/位图 PNG 的真实像素尺寸必须等于 manifest 的 `asset_pixel_width/height`，页面显示尺寸必须等于对应元素外框 `css_display_width/height`。
- `assets/icons/` 和 `assets/illustrations/` 中的 PNG 除非被明确记录为照片/截图/矩形背景素材，否则必须通过透明背景审计；带完整白底、灰底、页面底色或卡片底色矩形视为失败。
- 放入页面后任一高清 PNG 仍明显发糊，判定失败，必须提高 `asset_scale_factor` 或重新获取更高清源素材。
- 位图/图标必须保留完整透明留白和边缘像素，禁止自动裁边、智能缩边、内容自适应裁剪。
- 位图/图标 PNG 中如有非透明像素贴到画布边缘，默认视为裁切失败，必须扩大边界重出图，除非原图元素本身明确被父容器裁切。
- 任一图标、头像、插画、状态栏、导航图标不是来自当前源图，且与原图形状/比例/风格不完全一致，判定失败。
- 任一卡片插画的位置、大小、露出区域、裁切方式与原图不一致，判定失败。
- 任一模块因为自动排版导致整体坐标、间距、宽高和原图不一致，判定失败。
- 最终页面由切图、矢量和文本拼装后，必须与 750px 原图全覆盖复核，无缺图、无裁切、无错位、无层级错误。

## 交付说明

完成后只需要简短说明：

- 修改或新增的代码文件
- 切图资源目录
- 750px 画板尺寸
- `layers.manifest.json`
- bbox 预览图或等效框选复核说明
- 做过哪些截图和模块校验
- 做过哪些手机端宽度校验，尤其是 375px 的实际渲染宽度、缩放比例和横向溢出检查
- `audit_png_assets.py` 或等效 PNG 边缘/尺寸审计结果
- 是否已导出 Figma 可编辑 layer spec/importer；如已直接写入 Figma，提供 Figma 导入报告
- 已知限制，例如缺少原字体、源图像素不足、部分元素被遮挡

不要写冗长解释。真正的交付证明是代码、切图资源和复核截图。
