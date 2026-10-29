"""Fill template.html with the map and examples from mock.json; write site/index.html."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLOURS = {"3": "#3d5a7a", "2.4": "#33506f", "1.8": "#2a4566", "1.1": "#22395a",
           "0.9": "#1f3553", "0.8": "#1f3553", "0.5": "#182b44"}

m = json.loads((ROOT / "mock.json").read_text())
layers = "".join(
    f'<path d="{d}" stroke="{COLOURS.get(k, "#22395a")}" stroke-width="{float(k) * 1.3:.1f}" '
    'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    for k, d in sorted(m["layers"].items(), key=lambda kv: float(kv[0])))
lote = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#F2A65A" fill-opacity=".85" stroke="#0B1420" stroke-width="1.5"/>'
               for x, y in m["lote"])
labels = "".join(f'<text x="{l["x"]}" y="{l["y"]}" transform="rotate({l["a"]} {l["x"]} {l["y"]})" text-anchor="middle" dy="-4">{l["t"]}</text>' for l in m["labels"])
examples = {"ex": m["ex"], "route": {k: v for k, v in m["route"].items() if k != "line"}}
page = (ROOT / "template.html").read_text()
for key, value in {"__VW__": str(m["vw"]), "__VH__": str(m["vh"]), "__SEA__": m["sea"], "__LAYERS__": layers,
                   "__LOTE__": lote, "__LABELS__": labels, "__ROUTE__": m["route"]["line"],
                   "__EXJSON__": json.dumps(examples, ensure_ascii=False)}.items():
    page = page.replace(key, value)
(ROOT / "site" / "index.html").write_text(page)
print(f"site/index.html: {len(page) // 1024} KB")
