"""手画立绘的工具：每只幻兽用矢量曲线逐个部件画出来，这里负责明暗、描边、动画变换和转像素。

部件 part(d, 主色, 暗色)：先整块涂暗色，再把同一形状往左上挪一点涂主色，裁在原形状里，
得到右下方一道月牙形阴影（像宝可梦第五世代立绘那样的两三阶色块）；再沿轮廓描一圈深色线。
坐标系是 96x96，原点左上，脚底大约在 y=90。
渲染：Chromium 按 crispEdges 直接画成 96 像素（不抗锯齿），再把每个像素吸附到 SVG 里用过的颜色上，
最外一圈像素统一压成描边色。
"""
import json
import math
import os
import re
import subprocess
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 96
FRAMES = 24


def ell(cx, cy, rx, ry):
    """椭圆转成路径"""
    return f"M{cx - rx:.2f},{cy:.2f} a{rx:.2f},{ry:.2f} 0 1,0 {2 * rx:.2f},0 a{rx:.2f},{ry:.2f} 0 1,0 {-2 * rx:.2f},0 Z"


def poly(*pts):
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"


def rot(a, cx, cy):
    return f"rotate({a:.2f} {cx:.2f} {cy:.2f})"


def scale_about(sx, sy, cx, cy):
    return f"translate({cx:.2f} {cy:.2f}) scale({sx:.4f} {sy:.4f}) translate({-cx:.2f} {-cy:.2f})"


class Sprite:
    def __init__(self, outline="#2a1a24"):
        self.defs = []
        self.body = []
        self.stack = []
        self.n = 0
        self.outline = outline
        self.fit = 1.0  # 整只缩放（绕脚底中心），画大了超出画布时用

    def group(self, transform=""):
        """with s.group("rotate(...)"): 里面的部件一起变换"""
        sp = self

        class G:
            def __enter__(self_):
                sp.body.append(f'<g transform="{transform}">' if transform else "<g>")

            def __exit__(self_, *a):
                sp.body.append("</g>")
        return G()

    def part(self, d, base, shade=None, hi=None, line=None, off=(-2.2, -2.4), hi_off=None, lw=1.0):
        """一个上了明暗的部件。hi 给了就在左上再叠一小块高光"""
        self.n += 1
        cid = f"c{self.n}"
        self.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        g = [f'<g clip-path="url(#{cid})">', f'<path d="{d}" fill="{shade or base}"/>',
             f'<path d="{d}" fill="{base}" transform="translate({off[0]} {off[1]})"/>']
        if hi:
            ho = hi_off or (off[0] * 2.6, off[1] * 2.6)
            g.append(f'<path d="{d}" fill="{base}" transform="translate({ho[0]} {ho[1]})"/>')
            # 高光：原形状和往右下大幅偏移后的形状的差集太难算，改成在左上角叠一块缩小的形状
            g.append(f'<path d="{d}" fill="{hi}" transform="{_shrink_toward(d, .38)}"/>')
        g.append("</g>")
        if line != "none":
            g.append(f'<path d="{d}" fill="none" stroke="{line or self.outline}" stroke-width="{lw}" stroke-linejoin="round"/>')
        self.body.append("".join(g))

    def flat(self, d, fill, line=None, lw=1.0):
        """不上明暗的平涂块（花纹、肚皮里的小块）"""
        stroke = f' stroke="{line}" stroke-width="{lw}"' if line else ""
        self.body.append(f'<path d="{d}" fill="{fill}"{stroke} stroke-linejoin="round"/>')

    def line(self, d, color=None, w=1.0):
        self.body.append(f'<path d="{d}" fill="none" stroke="{color or self.outline}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')

    def eye(self, cx, cy, rx, ry, iris, blink=False, look=-0.35, pupil="#1a1020", tilt=0.0, lid=0.0):
        """动漫式大眼：眼白、虹膜（下半部亮）、瞳孔、两个高光；lid>0 时上眼皮压下来（凶）"""
        if blink:
            self.line(f"M{cx - rx},{cy + ry * .1} Q{cx},{cy + ry * .55} {cx + rx},{cy + ry * .1}", self.outline, 1.2)
            return
        t = f' transform="{rot(tilt, cx, cy)}"' if tilt else ""
        self.body.append(f"<g{t}>")
        self.flat(ell(cx, cy, rx, ry), "#ffffff", self.outline, 1.0)
        ix = cx + look * rx * .35
        self.flat(ell(ix, cy + ry * .08, rx * .72, ry * .8), iris)
        self.flat(ell(ix, cy + ry * .38, rx * .5, ry * .35), _lighten(iris, .35))
        self.flat(ell(ix, cy + ry * .02, rx * .36, ry * .45), pupil)
        self.flat(ell(ix - rx * .3, cy - ry * .32, rx * .26, ry * .24), "#ffffff")
        self.flat(ell(ix + rx * .25, cy + ry * .38, rx * .12, ry * .1), "#ffffff")
        if lid:
            self.flat(f"M{cx - rx - .5},{cy - ry - .5} L{cx + rx + .5},{cy - ry - .5} L{cx + rx + .5},{cy - ry + ry * 2 * lid * .6} "
                      f"L{cx - rx - .5},{cy - ry + ry * 2 * lid} Z", self.lid_color if hasattr(self, "lid_color") else self.outline)
            self.line(f"M{cx - rx - .3},{cy - ry + ry * 2 * lid} L{cx + rx + .3},{cy - ry + ry * 2 * lid * .6}", self.outline, 1.2)
        self.body.append("</g>")

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}" '
                f'shape-rendering="crispEdges"><defs>{"".join(self.defs)}</defs>'
                f'<g transform="{scale_about(self.fit, self.fit, SIZE / 2, SIZE - 5)}">{"".join(self.body)}</g></svg>')


def _lighten(h, t):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * t) for c in (r, g, b))


def _bbox(d):
    nums = [float(x) for x in re.findall(r"-?\d+\.?\d*", d)]
    # 只对绝对坐标的路径（M/L/C/Q 和 ell 生成的）估个大概：取所有成对数字
    xs, ys = nums[0::2], nums[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def _shrink_toward(d, k):
    """把形状缩小到 k 倍，并贴到原形状的左上部（做高光）"""
    if d.startswith("M") and " a" in d:  # ell() 生成的椭圆
        m = re.match(r"M(-?[\d.]+),(-?[\d.]+) a([\d.]+),([\d.]+)", d)
        x0, cy, rx, ry = (float(v) for v in m.groups())
        cx = x0 + rx
        tx, ty = cx - rx * .42, cy - ry * .45
    else:
        x0, y0, x1, y1 = _bbox(d)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        tx, ty = cx - (x1 - x0) * .22, cy - (y1 - y0) * .25
    return f"translate({tx:.2f} {ty:.2f}) scale({k}) translate({-cx:.2f} {-cy:.2f})"


# ------------------------------------------------------------------ 渲染
def render(jobs):
    """jobs: [(输出路径, [svg 字符串...])]，每个输出是一条横排"""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump([{"out": o, "size": SIZE, "frames": fr} for o, fr in jobs], f)
        path = f.name
    subprocess.run(["node", os.path.join(HERE, "render_svg.js"), path], check=True)
    os.unlink(path)
    for out, frames in jobs:
        cols = set()
        for svg in frames[:1]:
            cols |= set(re.findall(r'#[0-9a-fA-F]{6}', svg))
        clean(out, sorted(cols))


def clean(path, palette):
    """把像素吸附到调色板上，去掉半透明；最外一圈压成描边色"""
    im = Image.open(path).convert("RGBA")
    pal = [tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in palette]
    px = im.load()
    w, h = im.size
    cache = {}
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 110:
                px[x, y] = (0, 0, 0, 0)
                continue
            key = (r, g, b)
            if key not in cache:
                cache[key] = min(pal, key=lambda p: (p[0] - r) ** 2 + (p[1] - g) ** 2 + (p[2] - b) ** 2) if pal else key
            px[x, y] = cache[key] + (255,)
    darkest = min(pal, key=sum) if pal else (0, 0, 0)
    src = im.copy().load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                continue
            fx = x % SIZE
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx % SIZE == 0 and dx == 1 and fx == SIZE - 1) or src[nx, ny][3] == 0:
                    px[x, y] = darkest + (255,)
                    break
    im.save(path)


def anim(f):
    """第 f 帧的通用动画参数：breath 0→1→0（呼吸），sway 左右摆，flap 一个循环扇两次，blink 眨眼"""
    ph = f / FRAMES * 2 * math.pi
    return {"f": f, "ph": ph, "breath": (1 - math.cos(ph)) / 2, "sway": math.sin(ph), "flap": math.sin(ph * 2),
            "blink": f in (14, 15), "flick": math.sin(ph * 3)}
