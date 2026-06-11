---
name: case-card-h5
description: |
  单客户案例交互卡（飞书暗色风 1920×1080 H5）：之前痛点图 / 之后价值链路 /
  案例实证三态切换 + 断点诊断 + 截图灯箱 + 视频证据 + 入场动效。触发词：
  "案例卡"、"案例 H5"、"之前之后对比页"、"做成鹏飞那种案例页"。
  分工：底座与论证骨架冻结、编辑纪律靠校验、视觉隐喻放开（内置版式填数据，
  新隐喻走 raw 在底座上作图）。多页演示 deck 不归这里 —— 那是 feishu-deck-h5。
---

# case-card-h5

把一个客户案例做成一张可交互的深色 H5 案例卡。这个 skill 不追求"小模型一把过"，
它追求**用合适的约束把人工迭代和规整的活儿减到最少**。约束按层下手，松紧不同：

## 四层约束（这是全部心法，先读这段）

| 层 | 约束强度 | 它是什么 | 你能不能动 |
| --- | --- | --- | --- |
| **底座 substrate** | **死冻** | `template.html` 里的 token、stage 缩放、面板 chrome、连线工具、灯箱、动效 | 不能。觉得不够用就停下报告，别现场魔改 |
| **论证骨架** | **冻形状** | 三幕脊柱(之前/之后/实证) + 之前=带三联诊断的定位断点 + 之后=同对象的输入/中枢/闭环 | 不能改形状。schema 把它焊死 |
| **编辑纪律** | **启发+校验** | 前后同对象押韵、数字痛-收-证三连、证据即证明、零编造 | 你负责做到，validator 帮你兜 |
| **视觉隐喻** | **放开** | 用什么图讲"之前/之后"——泳道？组织树？网络拓扑？时间线？ | **自由**。这是手艺和差异该住的地方 |

一句话：**要约束的不是"画成什么样"，是"论证有没有骨头、文案有没有诚信"。** 视觉
留给你在底座上发挥——底座兜一致、骨架兜论证、validator 兜诚信，三道闸都不在视觉那层。

## 两条产出路径

每一幕（之前/之后/实证）二选一：

### A · 数据路径（命中内置版式，首选）

案例的这一幕能套内置版式，就只填数据，零视觉工作。版式目录（都自动排布、不手写坐标）：

| 幕 | 版式 | 形状 | 适用 |
| --- | --- | --- | --- |
| 之前 | **swimlane**（默认） | 阶段 × 泳道节点矩阵 + 连线 + 断点→三联诊断 | 单链路按阶段推进（鹏飞） |
| 之前 | **column-network** | N 列（列内 flat 节点或分组卡）+ 跨列任意连线 + 断点→诊断 | 多角色/多组织/多环节旧链路（广丰、永卓） |
| 之后 | **hub-3col**（默认） | 输入 → AI 中枢 → 业务闭环扇入扇出 + 右侧指标 | 输入汇聚到中枢再分发（鹏飞） |
| 之后 | **journey** | 轨 + N 张等宽卡（角色/标题/前后/证据图）+ 可选右侧指标 | 一个角色一天 / 一条流程怎么变好（广丰、永卓） |
| 实证 | **evidence**（默认） | 实证链路 + 视频/大图 + 截图 2×2 + 价值条 | 证据成链（通用） |

引擎自带**自适应排布**：模块位置/间距、断点沟槽、同类图等高、同层级字号——都由引擎按
该结构测量决定（同结构内同级一致，随结构自适应，不写死字号）。你只给数据，不给尺寸坐标。

版式用 `"layout"` 指定（默认值见上表，可省略）。同一幕选哪个版式，取决于案例的**自然形状**，不是花样。
填对应结构的 JSON 即可（字段见 schema；全内置版式范例见 `examples/pengfei.json`，
column-network + journey 范例见 `examples/yongzhuo.json`）。

### B · 授权作图（raw，需要新视觉隐喻时）

案例的某一幕**天生不是内置版式的形状**（鹏飞是泳道，但广丰更像组织树，北汽更像
网络拓扑），就给这一幕写 `"layout": "raw"`，在底座之上自己写版式：

```jsonc
"before": {
  "layout": "raw",
  "label": "组织树",
  "html": "<div class='layout'><section class='map-panel'>…用 .pain-node/.node 等底座类、var(--token) 着色…</section><aside class='side-panel'>…</aside></div>",
  "css": "/* 可选，颜色优先 var(--token)，类名加案例前缀防冲突 */",
  "js": "var map=pane.querySelector('.tree');var svg=CaseCard.svg(map,true);…CaseCard.drawEdges(svg,map,nodes,edges,'draw');"
}
```

完整可跑的范例见 `examples/raw-pane-demo.json`（一棵组织树，证明同底座能长出
swimlane 之外的视觉）。raw 幕仍然受底座 token、连线工具、动效、灯箱、validator 约束
—— **自由的是版式，不是品牌与诚信。**

**`CaseCard` 底座 API**（raw 的 `js` 里用，`new Function(pane, CaseCard)` 注入；
`pane` = 该 `.raw-pane` 元素）：

| API | 作用 |
| --- | --- |
| `CaseCard.svg(container, withArrow)` | 在容器里建一张 `.net-lines` SVG（withArrow=带箭头 marker） |
| `CaseCard.drawEdges(svg, container, nodeMap, edges, anim)` | **运行时实测**两节点矩形画连线，`edges=[{from,to,kind,anim}]`。节点位置变了线自动跟随——别手写坐标连线 |
| `CaseCard.reveal(node, i)` | 标记元素做入场错落动画（`--i` 控制次序） |
| `CaseCard.lightbox(src, caption)` | 打开灯箱。截图卡直接加 `data-full`/`data-caption` 属性即自动绑定，无需调它 |
| `CaseCard.rect / path / curve / routeOrtho / el / esc` | 测量、低层画线、建元素、转义 |

raw 的硬坑：**`html` 里的 `<script>` 不执行**（innerHTML 注入），脚本必须放 `js`
字段（也只有放 `js` 才能 round-trip，重建不丢）。

### 选哪条 + 目录怎么长

- **默认走 A。** 只有当案例自然形状确实不是内置版式时才走 B，并说清为什么。
- **别为了花样走 B**（换个字体、换个配色不算理由，那是漂移）。
- 某个 raw 隐喻在 **≥2 个案例**复现了，再考虑把它固化成新的内置版式（像
  swimlane/hub-3col 一样进目录）——挣到了再固化，别预先写死。

## 铁律（违反任何一条 = 返工）

1. **不改 `template.html`。** 底座死冻。新视觉走 raw，不是改底座。
2. **数据路径不写坐标；raw 连线用 `CaseCard.drawEdges`。** 节点位置由 stage/lane
   或 raw 里的 flow/定位决定，连线一律实测生成。JSON 数据字段里出现像素数字（除
   断点 offset 微调）就是走错了。
3. **不编造事实。** 没有的指标不写，没有的来源不标，没有的截图不引用。占位文案
   （TBD/待补/XXX）禁止进 JSON。
4. **超预算文案必须压缩。** validator 的 WARN 几乎全是"文字超盒子"——超长是破版
   第一原因。压文案，别想着改盒子。
5. **toggle 沿用"之前/之后/案例实证"导航语义。** label 是给读者的导航，**不要**填
   内部视觉隐喻名（执行树/闭环链/网络图）。读者要看的是对比逻辑，不是你用了什么版式。
   即使某幕走 raw，toggle 也照旧说"之前/之后"。

## 工作流（三步，单线程）

```bash
# 1. 读材料，写 JSON（每一幕选 A 或 B；见上文「内容塑形清单」）
#    资产路径相对"输出 HTML 所在目录"书写

# 2. 校验，修到 0 ERROR、尽量 0 WARN
python validate.py <case>.json --assets <输出目录>

# 3. 构建到资产旁边，浏览器里三个 pane 各看一眼
python build.py <case>.json <输出目录>/index.html
```

目测（每个 pane 用 hash 直达 `#before` / `#after` / `#evidence`）：节点不溢出、
断点 pill 不压字、连线锚在节点上、点断点右侧诊断对得上、截图点开灯箱正常。

## 交付与验收（给用户看什么）

**JSON 是源码，HTML 是交付物。** 只交 JSON 等于交了没编译的源码，任务不算完。

1. **正式**：跑完工作流，把 `<输出目录>/index.html` 给用户，三幕用 hash 直达。
2. **无 Python 时快速预览**：双击 `template.html`，点"选择本地 JSON 直接预览"（或拖
   JSON 进面板）。版式/文案/交互/动效即时可看；图片视频因相对路径可能不显示，属
   预期，资产以正式构建为准。

## 内容塑形清单（成片质量在这里，不在代码）

- **header.title 是论点不是题目**："围绕 X，构建 Y 闭环" 强于 "X 公司案例介绍"。
- **之前讲链路断点**：先把旧流程拆成阶段 × 泳道（或一棵树/一张网）的节点结构，再问
  "链条在哪几处断了"——每个断点配反问句标题 + 根本原因/业务影响/关键后果三联卡。
  dim 掉非焦点节点，留 1-2 个亮节点做视觉起点。
- **之后讲同一条链怎么被接通**：输入必须能和"之前"的节点对上（同一批业务对象），
  闭环用统一句式（"XX闭环"），指标必须含数字且写对比口径（"4 小时 → 1 分钟"比
  "大幅提升"有力 10 倍）。
- **实证是证据链不是截图堆**：logic.steps 先立"要证明什么"，视频/截图按步骤对号入
  座；每条证据写"它证明了什么"，不是"这是什么页面"。
- **数字三处呼应**：之前埋的痛（30 分钟响应）→ 之后指标收（3 分钟）→ 实证再证
  （3 分钟）。同一组数字穿过三幕，才有"闭环"体感。

## 形态不符时

- 案例没有"之前/之后"对比、只是单线故事 → 用 feishu-deck-h5 的 one-pager
  story-case（痛点/冲突/解法/价值四拍），别硬掰成三幕。
- 需要多页演示、章节、封面 → feishu-deck-h5。
- 案例的某一幕需要全新视觉隐喻 → **不是**去 feishu-deck-h5，是本 skill 的 raw 路径。
- 四张以上案例卡合集 → 每案例一个文件夹 + 顶层 tab/iframe 壳（参考仓库根
  index.html），不要往一张卡里塞两个客户。

## 文件清单

```
case-card-h5/
  SKILL.md                      ← 本文件
  template.html                 ← 底座 + 内置版式目录（CSS+JS+数据岛），死冻勿改
  build.py                      ← JSON 注入数据岛 → 输出 HTML
  validate.py                   ← 结构 ERROR + 文案预算 WARN + 资产存在性 + raw 检查
  schema/case-card.schema.json  ← 数据契约（内置版式字段 + rawPane，含每字段预算）
  examples/                     ← 四个真实案例 + raw 范例，覆盖全部 5 版式；见 examples/README.md
    pengfei.json   鹏飞（swimlane + hub-3col + evidence）
    yongzhuo.json  永卓（column-network + journey + evidence）
    gac-toyota.json 广丰（column-network + journey + evidence）
    beiqi.json     北汽（column-network + hub-3col + evidence）
    raw-pane-demo.json  raw 授权作图（组织树）
    README.md      覆盖表 + 资产另放约定（客户案例不带资产，--skip-assets 校验结构）
```
