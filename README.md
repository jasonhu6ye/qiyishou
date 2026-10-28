# 奇异兽

一款类 PokeMMO 的 2.5D 俯视角怪兽收集 RPG，用 Godot 4 开发。当前是单机可玩的最小版本。画面以 320×240 渲染再整数倍放大，地面、树和人物是像素图，房屋和奇异兽还是代码绘制的占位图。

![大地图](docs/screenshots/world.png)
![战斗](docs/screenshots/battle.png)

## 运行

1. 安装 [Godot 4.3](https://godotengine.org/download)（标准版即可，不需要 .NET 版）。
2. 打开 Godot，导入本仓库根目录下的 `project.godot`。
3. 按 F5 运行。

| 操作 | 按键 |
| --- | --- |
| 移动 | WASD / 方向键 |
| 奔跑 | 按住 Shift |
| 对话、确认 | 空格 / Z / 回车 |
| 队伍菜单 | X / Esc |

## 目前有什么

- 晨露镇、1号道路、2号道路，带树木和房屋的 Y 排序遮挡（2.5D 效果）
- 走进高草有 12% 概率遇到野生奇异兽，两条道路的等级和物种不同
- 回合制战斗：火 → 草 → 水 → 火 属性克制、本系加成、会心一击、按速度决定先后手
- 兽球捕捉（血越少越好抓）、6 只队伍上限、存储箱
- 经验、升级、学新招式
- 治疗所恢复、NPC 对话、自动存档（`user://save.json`）

## 目录结构

```
project.godot
scenes/main.tscn          主场景（只挂了 main.gd，其余节点在代码里创建）
scripts/
  game.gd                 全局状态（自动加载为 Game）：队伍、道具、图鉴、存档、按键
  data.gd                 招式、属性克制、物种、遭遇表
  monster.gd              奇异兽实例：能力值、升级、序列化
  art.gd                  占位美术（人物、树、房屋、奇异兽）
  main.gd                 主流程：行走 / 对话 / 战斗 / 菜单 切换
  world/world.gd          地图生成与地面绘制，Y 排序物件层
  world/player.gd         网格移动的玩家与相机
  world/prop.gd           树、房屋、NPC
  battle/battle.gd        战斗逻辑
  battle/battle_view.gd   战斗画面绘制
  ui/dialog_box.gd        对话框与选项按钮
  ui/hud.gd               状态栏与地名提示
assets/sprites/           像素图：tiles.png 地面图块、tree.png、player.png / npc_elder.png 行走图
assets/fonts/             Fusion Pixel 12px 中文像素字体（SIL OFL 1.1，见 OFL.txt）
tools/gen_pixel_art.py    重新生成 assets/sprites 下的像素图（需要 Pillow）
tests/smoke_test.tscn     冒烟测试
tests/screenshot.tscn     截图脚本（CI 用虚拟显示器运行，截图作为构建产物上传）
```

## 美术规格

- 渲染分辨率 320×240，窗口 960×720，整数倍缩放，关闭纹理过滤
- 图块 16×16。`tiles.png` 一行依次是：草地、草地变体、花、高草、小路、水面三帧、高草前景
- 人物行走图每帧 16×20，3 列（站立、迈左脚、迈右脚）× 4 行（下、左、右、上）
- 树 16×32，原点在底边中心
- 字体只用 12px（或 24px 等整数倍），否则像素会糊

换手绘图时保持同样的尺寸和排布，代码不用改。

## 测试

每次推送，GitHub Actions 会下载 Godot 4.3，在无头模式下导入项目并运行冒烟测试（数据公式、存档读写、主场景加载、自动打完一场战斗）。本地运行：

```
godot --headless --path . res://tests/smoke_test.tscn
```

## 路线图

1. **美术**：房屋改成像素图、奇异兽正面/背面像素图、战斗背景图、地图改用 TileMapLayer 方便在编辑器里画
2. **内容**：更多物种和招式、进化、道具与商店、训练师对战、第二个城镇
3. **系统**：状态异常、能力等级变化、特性、图鉴界面
4. **联机**（单机打磨好之后）：同屏看到其他玩家、交易、玩家对战。届时需要单独的服务器
