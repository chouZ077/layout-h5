#!/usr/bin/env python3
"""case-card-h5 builder: inject a case JSON into template.html's data island.

Usage:
    python build.py <data.json> <output.html>

Output path matters: asset paths inside the JSON resolve relative to the
output HTML, so build next to the assets folder they reference.
"""
import json
import re
import sys
from pathlib import Path

ISLAND_RE = re.compile(
    r'(<script type="application/json" id="case-data">).*?(</script>)', re.S
)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip())
        return 2
    data_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    template = Path(__file__).parent / "template.html"

    data = json.loads(data_path.read_text(encoding="utf-8"))
    html = template.read_text(encoding="utf-8")

    # </ must not appear literally inside a <script> block; \/ is valid JSON.
    payload = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")

    html, n = ISLAND_RE.subn(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(2), html)
    if n != 1:
        print(f"ERROR: expected exactly 1 data island in template, found {n}")
        return 1

    title = data.get("doc_title") or data.get("header", {}).get("title", "Case Card")
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.S)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"BUILT {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
