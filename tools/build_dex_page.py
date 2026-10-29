"""把 data/dex/ 的规划数据嵌进图鉴页面，输出 build/naers-dex.html（单文件，立绘图集以 data URI 嵌在里面，浏览器直接打开）。

python3 tools/dex_plan.py && python3 tools/gen_species_art.py && python3 tools/build_dex_page.py
"""
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import world_plan as wp  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PER, FW, NF, BW, BCOLS = 180, 72, 24, 96, 24  # 和模板里的常量一致


def build_atlas(species, out):
    """正面每 PER 只一张（一只一行 NF 帧），背面一张（BCOLS 列）"""
    os.makedirs(out, exist_ok=True)
    src = os.path.join(ROOT, "assets", "sprites", "dex")
    for n in range(0, len(species), PER):
        chunk = species[n:n + PER]
        im = Image.new("RGBA", (FW * NF, FW * len(chunk)))
        for r, sp in enumerate(chunk):
            im.paste(Image.open(os.path.join(src, sp["key"] + "_front.png")), (0, r * FW))
        im.save(os.path.join(out, f"front{n // PER}.webp"), lossless=True, quality=100, method=6)
    rows = (len(species) + BCOLS - 1) // BCOLS
    im = Image.new("RGBA", (BW * BCOLS, BW * rows))
    for i, sp in enumerate(species):
        im.paste(Image.open(os.path.join(src, sp["key"] + "_back.png")), ((i % BCOLS) * BW, (i // BCOLS) * BW))
    im.save(os.path.join(out, "back.webp"), lossless=True, quality=100, method=6)


def main():
    d = {k: json.load(open(os.path.join(ROOT, "data", "dex", k + ".json"), encoding="utf-8"))
         for k in ["types", "moves", "abilities", "species", "spawns"]}
    d["regions"] = [{"name": r["name"], "biome": r["biome"], "levels": list(r["levels"])} for r in wp.REGIONS]
    data = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    out_atlas = os.path.join(ROOT, "build", "atlas")
    build_atlas(d["species"], out_atlas)
    embed = {f"atlas/{n}": "data:image/webp;base64," + base64.b64encode(open(os.path.join(out_atlas, n), "rb").read()).decode()
             for n in sorted(os.listdir(out_atlas))}
    page = open(os.path.join(ROOT, "tools", "dex_page_template.html"), encoding="utf-8").read().replace("__DATA__", data).replace("__ATLAS__", json.dumps(embed))
    out = os.path.join(ROOT, "build", "naers-dex.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write("<!doctype html><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n" + page)
    print(out)


if __name__ == "__main__":
    main()
