"""手画立绘批量渲染：python3 tools/hand/build.py [key ...]
输出 assets/sprites/dex/<key>_front.png（24 帧横排，每帧 96x96）"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402

MODULES = ["fox", "frog", "mouse", "legends1", "legends2"]
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "assets", "sprites", "dex")


def all_species():
    out = {}
    for m in MODULES:
        out.update(importlib.import_module(m).SPECIES)
    return out


def main(keys=None, out_dir=OUT):
    sp = all_species()
    keys = keys or list(sp)
    os.makedirs(out_dir, exist_ok=True)
    jobs = [(os.path.join(out_dir, f"{k}_front.png"), [sp[k](f).svg() for f in range(kit.FRAMES)]) for k in keys]
    kit.render(jobs)
    return keys


if __name__ == "__main__":
    main(sys.argv[1:] or None)
