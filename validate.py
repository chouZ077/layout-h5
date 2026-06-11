#!/usr/bin/env python3
"""case-card-h5 validator.

ERROR  = structural problem, build will look broken -> must fix.
WARN   = content budget exceeded, likely overflow/crowding -> shorten copy.

Usage:
    python validate.py <data.json> [--assets DIR]

--assets DIR : directory that relative asset paths (videos/shots/hero) resolve
               against — i.e. the directory the output HTML will be built into.
               Default: the JSON file's own directory.
"""
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def width(text: str) -> float:
    """显示宽度：全角算 1，半角算 0.5 —— 预算按全角字符数定。"""
    return sum(1.0 if ord(c) > 0x2E7F else 0.5 for c in text)

# (json-path-ish, budget in full-width chars) — soft limits tuned to the
# frozen template's boxes; exceeding them is the #1 cause of broken layout.
BUDGETS = {
    "header.title": 32,
    "header.sub": 140,
    "before.banner.title": 14,
    "before.banner.desc": 64,
    "before.node.title": 12,
    "before.node.desc": 26,
    "before.breakpoint.label": 14,
    "before.detail.title": 22,
    "before.detail.summary": 60,
    "before.detail.card.text": 90,
    "after.input.title": 12,
    "after.input.desc": 26,
    "after.hub.core.desc": 50,
    "after.hub.cell.desc": 44,
    "after.output.title": 12,
    "after.output.desc": 30,
    "after.side.title": 20,
    "after.side.copy": 90,
    "after.metric.title": 16,
    "after.metric.desc": 48,
    "after.journey.eyebrow": 18,
    "after.journey.title": 18,
    "after.journey.compare": 64,
    "after.journey.note": 30,
    "after.rail": 10,
    "evidence.head.title": 40,
    "evidence.head.desc": 90,
    "evidence.step.desc": 45,
    "evidence.video.desc": 90,
    "evidence.shot.title": 12,
    "evidence.shot.desc": 30,
    "evidence.value.desc": 40,
}

errors: list[str] = []
warns: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warns.append(msg)


def budget(key: str, text, where: str) -> None:
    if isinstance(text, str) and key in BUDGETS and width(text) > BUDGETS[key]:
        warn(f"{where}: 宽 {width(text):.0f} > 预算 {BUDGETS[key]} —— 「{text[:18]}…」")


def need(obj: dict, field: str, where: str):
    v = obj.get(field)
    if v in (None, "", [], {}):
        err(f"{where}: 缺少必填字段 `{field}`")
    return v


SKIP_ASSETS = False  # --skip-assets：example 不带资产时跳过存在性检查（结构仍校验）


def check_asset(path_str, assets_dir: Path, where: str) -> None:
    if SKIP_ASSETS:
        return
    if not isinstance(path_str, str) or not path_str:
        return
    if path_str.startswith(("http://", "https://", "data:")):
        return
    if not (assets_dir / path_str).exists():
        err(f"{where}: 资产不存在 `{path_str}`（相对 {assets_dir}）")


def check_breakpoints(bps: list, keys: set, prefix: str) -> None:
    """断点 + 三联诊断校验（swimlane / column-network 共用）。"""
    if not (2 <= len(bps) <= 5):
        warn(f"{prefix}.breakpoints: {len(bps)} 个，推荐 3-4")
    bp_keys: set[str] = set()
    for i, bp in enumerate(bps):
        w = f"{prefix}.breakpoints[{i}]"
        k = need(bp, "key", w)
        need(bp, "label", w)
        if k in bp_keys:
            err(f"{w}: key `{k}` 重复")
        bp_keys.add(k)
        budget("before.breakpoint.label", bp.get("label"), f"{w}.label")
        between = bp.get("between") or []
        if len(between) != 2 or any(x not in keys for x in between):
            err(f"{w}: between 必须是 2 个已声明的 node key，得到 {between!r}")
        for x in bp.get("related") or []:
            if x not in keys:
                err(f"{w}: related 含未知 node key `{x}`")
        detail = need(bp, "detail", w) or {}
        need(detail, "title", f"{w}.detail")
        budget("before.detail.title", detail.get("title"), f"{w}.detail.title")
        budget("before.detail.summary", detail.get("summary"), f"{w}.detail.summary")
        cards = need(detail, "cards", f"{w}.detail") or []
        if len(cards) != 3:
            warn(f"{w}.detail.cards: {len(cards)} 张，规范是 根本原因/业务影响/关键后果 三张")
        for j, c in enumerate(cards):
            need(c, "label", f"{w}.detail.cards[{j}]")
            need(c, "text", f"{w}.detail.cards[{j}]")
            budget("before.detail.card.text", c.get("text"), f"{w}.detail.cards[{j}].text")


def check_before_network(b: dict, assets: Path) -> None:
    """column-network：列式网络。列内流式排布，校验列/分组/连线/断点。"""
    columns = need(b, "columns", "before") or []
    if not (2 <= len(columns) <= 5):
        warn(f"before.columns: {len(columns)} 列，推荐 3-4")
    keys: set[str] = set()
    for ci, col in enumerate(columns):
        budget("after.side.title", col.get("title"), f"before.columns[{ci}].title")
        items = need(col, "items", f"before.columns[{ci}]") or []
        for ii, it in enumerate(items):
            w = f"before.columns[{ci}].items[{ii}]"
            need(it, "title", w)
            budget("before.node.title", it.get("title"), f"{w}.title")
            budget("before.node.desc", it.get("desc"), f"{w}.desc")
            k = it.get("key")
            if k:
                if k in keys:
                    err(f"{w}: key `{k}` 重复")
                keys.add(k)
            if it.get("variant") not in (None, "sys", "warn"):
                err(f"{w}: variant 只能是 sys/warn")
            for ji, ch in enumerate(it.get("children") or []):
                cw = f"{w}.children[{ji}]"
                need(ch, "title", cw)
                budget("before.node.desc", ch.get("desc"), f"{cw}.desc")
    for i, e in enumerate(b.get("edges") or []):
        w = f"before.edges[{i}]"
        for f in ("from", "to"):
            if e.get(f) not in keys:
                err(f"{w}: `{f}`=`{e.get(f)}` 不是已声明的 item key（连线只能接有 key 的 item）")
        if e.get("kind") not in (None, "flow", "data"):
            err(f"{w}: kind 只能是 flow/data")
    check_breakpoints(need(b, "breakpoints", "before") or [], keys, "before")


def check_before(b: dict, assets: Path) -> None:
    stages = need(b, "stages", "before") or []
    lanes = need(b, "lanes", "before") or []
    nodes = need(b, "nodes", "before") or []
    if not (2 <= len(stages) <= 5):
        warn(f"before.stages: {len(stages)} 个，推荐 3-5")
    if not (1 <= len(lanes) <= 4):
        warn(f"before.lanes: {len(lanes)} 个，推荐 2-3")

    if b.get("banner"):
        budget("before.banner.title", b["banner"].get("title"), "before.banner.title")
        budget("before.banner.desc", b["banner"].get("desc"), "before.banner.desc")

    keys: set[str] = set()
    for i, n in enumerate(nodes):
        w = f"before.nodes[{i}]"
        k = need(n, "key", w)
        need(n, "title", w)
        if k in keys:
            err(f"{w}: key `{k}` 重复")
        keys.add(k)
        for f, hi in (("stage", len(stages)), ("lane", len(lanes))):
            v = n.get(f)
            if not isinstance(v, int) or not (0 <= v < hi):
                err(f"{w}: `{f}`={v!r} 越界（应为 0..{hi - 1} 的整数）")
        budget("before.node.title", n.get("title"), f"{w}.title")
        budget("before.node.desc", n.get("desc"), f"{w}.desc")
        if n.get("variant") not in (None, "sys", "warn"):
            err(f"{w}: variant 只能是 sys/warn")

    for i, e in enumerate(b.get("edges") or []):
        w = f"before.edges[{i}]"
        for f in ("from", "to"):
            if e.get(f) not in keys:
                err(f"{w}: `{f}`=`{e.get(f)}` 不是已声明的 node key")
        if e.get("kind") not in (None, "flow", "data"):
            err(f"{w}: kind 只能是 flow/data")

    check_breakpoints(need(b, "breakpoints", "before") or [], keys, "before")


def check_after(a: dict) -> None:
    inputs = need(a, "inputs", "after") or []
    outputs = need(a, "outputs", "after") or []
    hub = need(a, "hub", "after") or {}
    side = need(a, "side", "after") or {}
    if not (3 <= len(inputs) <= 7):
        warn(f"after.inputs: {len(inputs)} 个，推荐 5-6")
    if not (3 <= len(outputs) <= 6):
        warn(f"after.outputs: {len(outputs)} 个，推荐 4-5")
    for arr, prefix in ((inputs, "after.input"), (outputs, "after.output")):
        for i, n in enumerate(arr):
            w = f"{prefix}s[{i}]"
            need(n, "title", w)
            budget(f"{prefix}.title", n.get("title"), f"{w}.title")
            budget(f"{prefix}.desc", n.get("desc"), f"{w}.desc")
    core = need(hub, "core", "after.hub") or {}
    need(core, "title", "after.hub.core")
    budget("after.hub.core.desc", core.get("desc"), "after.hub.core.desc")
    cells = hub.get("cells") or []
    if len(cells) > 4:
        warn(f"after.hub.cells: {len(cells)} 张，推荐 ≤3")
    for i, c in enumerate(cells):
        need(c, "title", f"after.hub.cells[{i}]")
        budget("after.hub.cell.desc", c.get("desc"), f"after.hub.cells[{i}].desc")
    need(side, "title", "after.side")
    budget("after.side.title", side.get("title"), "after.side.title")
    budget("after.side.copy", side.get("copy"), "after.side.copy")
    metrics = need(side, "metrics", "after.side") or []
    if not (3 <= len(metrics) <= 6):
        warn(f"after.side.metrics: {len(metrics)} 张，推荐 4-5")
    for i, m in enumerate(metrics):
        w = f"after.side.metrics[{i}]"
        need(m, "title", w)
        need(m, "desc", w)
        budget("after.metric.title", m.get("title"), f"{w}.title")
        budget("after.metric.desc", m.get("desc"), f"{w}.desc")
        if isinstance(m.get("title"), str) and not any(ch.isdigit() for ch in m["title"]):
            warn(f"{w}.title: 指标卡标题不含数字 —— 「{m['title']}」；尽量给可量化口径")


def check_after_journey(a: dict, assets: Path) -> None:
    """journey：旅程时间线。轨可选，cards 必填，side 可选（沿用 metric 校验）。"""
    rail = a.get("rail") or []
    if rail and not (2 <= len(rail) <= 5):
        warn(f"after.rail: {len(rail)} 站，推荐 4")
    for i, r in enumerate(rail):
        budget("after.rail", r, f"after.rail[{i}]")
    cards = need(a, "cards", "after") or []
    if not (3 <= len(cards) <= 5):
        warn(f"after.cards: {len(cards)} 张，推荐 4（与 rail 站数一致最稳）")
    if rail and cards and len(rail) != len(cards):
        warn(f"after: rail {len(rail)} 站 与 cards {len(cards)} 张不一致，轨与卡建议一一对应")
    for i, c in enumerate(cards):
        w = f"after.cards[{i}]"
        need(c, "title", w)
        budget("after.journey.eyebrow", c.get("eyebrow"), f"{w}.eyebrow")
        budget("after.journey.title", c.get("title"), f"{w}.title")
        budget("after.journey.compare", c.get("before"), f"{w}.before")
        budget("after.journey.compare", c.get("after"), f"{w}.after")
        shot = c.get("shot")
        if shot:
            need(shot, "image", f"{w}.shot")
            check_asset(shot.get("image"), assets, f"{w}.shot.image")
            check_asset(shot.get("full"), assets, f"{w}.shot.full")
            budget("after.journey.note", shot.get("note"), f"{w}.shot.note")
    side = a.get("side")
    if side:
        need(side, "title", "after.side")
        budget("after.side.title", side.get("title"), "after.side.title")
        budget("after.side.copy", side.get("copy"), "after.side.copy")
        for i, m in enumerate(side.get("metrics") or []):
            w = f"after.side.metrics[{i}]"
            need(m, "title", w)
            need(m, "desc", w)
            budget("after.metric.title", m.get("title"), f"{w}.title")
            budget("after.metric.desc", m.get("desc"), f"{w}.desc")


def check_evidence(ev: dict, assets: Path) -> None:
    head = need(ev, "head", "evidence") or {}
    need(head, "title", "evidence.head")
    budget("evidence.head.title", head.get("title"), "evidence.head.title")
    budget("evidence.head.desc", head.get("desc"), "evidence.head.desc")
    videos = ev.get("videos") or []
    if len(videos) > 2:
        err(f"evidence.videos: 最多 2 条，得到 {len(videos)}")
    for i, v in enumerate(videos):
        w = f"evidence.videos[{i}]"
        need(v, "src", w)
        need(v, "title", w)
        check_asset(v.get("src"), assets, f"{w}.src")
        check_asset(v.get("poster"), assets, f"{w}.poster")
        budget("evidence.video.desc", v.get("desc"), f"{w}.desc")
    if not videos and not ev.get("hero"):
        warn("evidence: 既无 videos 也无 hero，中央证据区将为空")
    if ev.get("hero"):
        check_asset(ev["hero"].get("image"), assets, "evidence.hero.image")
        check_asset(ev["hero"].get("full"), assets, "evidence.hero.full")
    shots = ev.get("shots") or []
    if shots and len(shots) != 4:
        warn(f"evidence.shots: {len(shots)} 张，模板按 2×2 排版，推荐正好 4 张")
    for i, s in enumerate(shots):
        w = f"evidence.shots[{i}]"
        need(s, "image", w)
        need(s, "title", w)
        check_asset(s.get("image"), assets, f"{w}.image")
        check_asset(s.get("full"), assets, f"{w}.full")
        budget("evidence.shot.title", s.get("title"), f"{w}.title")
        budget("evidence.shot.desc", s.get("desc"), f"{w}.desc")
    values = ev.get("values") or []
    if values and len(values) != 4:
        warn(f"evidence.values: {len(values)} 格，推荐正好 4 格")
    for i, v in enumerate(values):
        w = f"evidence.values[{i}]"
        need(v, "title", w)
        need(v, "desc", w)
        budget("evidence.value.desc", v.get("desc"), f"{w}.desc")
    steps = (ev.get("logic") or {}).get("steps") or []
    for i, s in enumerate(steps):
        w = f"evidence.logic.steps[{i}]"
        need(s, "title", w)
        budget("evidence.step.desc", s.get("desc"), f"{w}.desc")


# before 可选 swimlane（默认）或 column-network；after 默认 hub-3col（journey 见下）。
BEFORE_LAYOUTS = {"swimlane": check_before, "column-network": check_before_network}
BUILTIN_LAYOUT = {"before": "swimlane", "after": "hub-3col", "evidence": "evidence"}


def check_raw(name: str, pane: dict, assets: Path) -> None:
    """layout:"raw" 授权作图 pane：只把住会真破/真坑的几条，版式本身放开。"""
    html = pane.get("html")
    if not isinstance(html, str) or not html.strip():
        err(f"{name}(raw): 缺少 `html` 字符串")
        return
    if "<script" in html.lower():
        err(f"{name}(raw): html 里的 <script> 不会执行（innerHTML 注入）；脚本放进 `js` 字段")
    for fld in ("css", "js"):
        if pane.get(fld) is not None and not isinstance(pane[fld], str):
            err(f"{name}(raw): `{fld}` 必须是字符串")
    css = pane.get("css") or ""
    hexes = sorted(set(re.findall(r"#[0-9a-fA-F]{3,8}\b", css)))
    if hexes:
        warn(f"{name}(raw): css 用裸色值 {hexes[:4]}；优先 var(--blue/--teal/--amber/--red…) 保持与底座一致")
    refs = re.findall(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', html)
    refs += re.findall(r'url\(\s*["\']?([^"\')]+)', html + css)
    for r in refs:
        check_asset(r, assets, f"{name}(raw) 资产")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--assets", help="目录：资产相对路径的解析基准（= 输出 HTML 所在目录）")
    ap.add_argument("--skip-assets", action="store_true",
                    help="跳过资产存在性检查（参考 example 不带图/视频时用）")
    args = ap.parse_args()

    global SKIP_ASSETS
    SKIP_ASSETS = args.skip_assets

    data_path = Path(args.data)
    assets = Path(args.assets) if args.assets else data_path.parent
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: JSON 解析失败: {e}")
        return 1

    header = need(data, "header", "$") or {}
    need(header, "title", "header")
    budget("header.title", header.get("title"), "header.title")
    budget("header.sub", header.get("sub"), "header.sub")

    panes = need(data, "panes", "$") or {}
    unknown = set(panes) - {"before", "after", "evidence"}
    if unknown:
        err(f"panes: 未知 pane {sorted(unknown)}（三幕脊柱只认 before/after/evidence）")
    # 每个 act 可以是内置版式（填数据）或 layout:"raw"（授权作图）。
    for name in ("before", "after", "evidence"):
        if name not in panes:
            continue
        pane = panes[name]
        lbl = pane.get("label")
        if isinstance(lbl, str) and lbl and not any(c in lbl for c in "前后证"):
            warn(f"{name}.label=「{lbl}」：toggle 是给读者的导航，应沿用 之前/之后/案例实证 语义；"
                 "别填内部视觉隐喻名（执行树/闭环链/网络图）")
        layout = pane.get("layout")
        if layout == "raw":
            check_raw(name, pane, assets)
        elif name == "before":
            fn = BEFORE_LAYOUTS.get(layout or "swimlane")
            if fn:
                fn(pane, assets)
            else:
                err(f"before.layout=`{layout}` 未知；只能是 swimlane / column-network / raw")
        elif name == "after":
            if layout in (None, "hub-3col"):
                check_after(pane)
            elif layout == "journey":
                check_after_journey(pane, assets)
            else:
                err(f"after.layout=`{layout}` 未知；只能是 hub-3col / journey / raw")
        elif name == "evidence":
            if layout in (None, "evidence"):
                check_evidence(pane, assets)
            else:
                err(f"evidence.layout=`{layout}` 未知；只能是 evidence / raw")
    if data.get("initial") and data["initial"] not in panes:
        err(f"initial=`{data['initial']}` 不在 panes 中")

    for e in errors:
        print(f"ERROR  {e}")
    for w in warns:
        print(f"WARN   {w}")
    print(f"\n{len(errors)} errors, {len(warns)} warnings — "
          + ("FAIL：先修 ERROR 再构建。" if errors else "PASS"
             + ("（有 WARN：建议压缩超预算文案，超长是破版第一原因）" if warns else "")))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
