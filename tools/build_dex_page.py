"""把 data/dex/ 的规划数据嵌进图鉴页面，输出 build/naers-dex.html（单文件，浏览器直接打开）。

python3 tools/dex_plan.py && python3 tools/build_dex_page.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import world_plan as wp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    d = {k: json.load(open(os.path.join(ROOT, "data", "dex", k + ".json"), encoding="utf-8"))
         for k in ["types", "moves", "abilities", "species", "spawns"]}
    d["regions"] = [{"name": r["name"], "biome": r["biome"], "levels": list(r["levels"])} for r in wp.REGIONS]
    data = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = open(os.path.join(ROOT, "tools", "dex_page_template.html"), encoding="utf-8").read().replace("__DATA__", data)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    out = os.path.join(ROOT, "build", "naers-dex.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write("<!doctype html><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n" + page)
    print(out)


if __name__ == "__main__":
    main()
