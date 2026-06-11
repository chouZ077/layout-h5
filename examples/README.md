# examples — 参考案例

四个真实客户案例 + 一个 raw 范例，覆盖全部 5 个内置版式与授权作图路径。
读它们学"一个真实案例怎么映射到本 skill 的版式"。

| 文件 | 案例 | 之前 | 之后 | 实证 |
| --- | --- | --- | --- | --- |
| `pengfei.json` | 鹏飞集团 AI 全维监测 | swimlane | hub-3col | evidence |
| `yongzhuo.json` | 永卓控股 高炉智析 | column-network | journey | evidence |
| `gac-toyota.json` | 广汽丰田 铂智3X 打铁专项 | column-network | journey | evidence |
| `beiqi.json` | 北汽福田 长超小福 | column-network | hub-3col | evidence |
| `raw-pane-demo.json` | raw 授权作图 demo | raw（组织树） | — | — |

## 资产（图片 / 视频）需另外放

这些客户案例的 JSON 里引用了 `assets/...` 路径（截图、视频），但**资产二进制不随包提供**。
要实际构建出带图的页面，把对应资产放到**输出 HTML 所在目录**旁，保持 JSON 里的相对路径：

```
<输出目录>/
  index.html              ← build.py 产出
  assets/source/iron-06.png   ← 按 JSON 里的路径放
  assets/cases/dashboard.jpg
  ...
```

- 想知道某个案例缺哪些资产：**不加** `--skip-assets` 跑校验，报告会列出全部缺失清单。
- 只校验结构（不管资产）：`python validate.py examples/gac-toyota.json --skip-assets`
- `raw-pane-demo.json` **无资产、开箱即跑**：
  `python build.py examples/raw-pane-demo.json out/index.html` 直接出图。

## 关于北汽（beiqi.json）

原始北汽案例的"之前/之后"是**同一张网络图原地变色**（morph）。本 skill 的三幕是独立切换、
不做 morph（见 SKILL.md），所以这里映射成 column-network(之前) + hub-3col(之后) 两张图——
内容完整保留，只是少了那层视觉变色过渡。这是已知的取舍，不是缺陷。
