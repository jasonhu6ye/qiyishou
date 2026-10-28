class_name TerrainAtlas
extends RefCounted
## 由 tools/gen_terrain.py 生成，不要手改。terrain.png 里每一块的位置（像素）。

## 基础地面，按绘制先后（后面的盖住前面的）。每行：4 个变体 + N S W E NW NE SW SE 过渡片
const BASES := ["sand", "mud", "ash", "rock", "grass", "forest", "snow"]
const BASE_Y := {"sand": 0, "mud": 16, "ash": 32, "rock": 48, "grass": 64, "forest": 80, "snow": 96}

## 自动拼接块（每帧 32x40）的左上角
const OVERLAY := {
	"path": [Vector2i(0, 112)],
	"water": [Vector2i(32, 112), Vector2i(64, 112), Vector2i(96, 112)],
	"deep": [Vector2i(128, 112), Vector2i(160, 112), Vector2i(192, 112)],
	"lava": [Vector2i(224, 112), Vector2i(256, 112), Vector2i(288, 112)],
	"bog": [Vector2i(320, 112), Vector2i(352, 112)],
	"ice": [Vector2i(0, 152)],
	"tall_grass": [Vector2i(32, 152), Vector2i(64, 152)],
	"tall_forest": [Vector2i(96, 152), Vector2i(128, 152)],
	"tall_swamp": [Vector2i(160, 152), Vector2i(192, 152)],
	"tall_coast": [Vector2i(224, 152), Vector2i(256, 152)],
	"tall_desert": [Vector2i(288, 152), Vector2i(320, 152)],
	"tall_volcano": [Vector2i(352, 152), Vector2i(0, 192)],
	"tall_mountain": [Vector2i(32, 192), Vector2i(64, 192)],
	"tall_lakes": [Vector2i(96, 192), Vector2i(128, 192)],
	"tall_snow": [Vector2i(160, 192), Vector2i(192, 192)],
}

## 16x16 单格贴图的左上角
const SINGLE := {
	"front_grass": Vector2i(0, 232),
	"front_forest": Vector2i(16, 232),
	"front_swamp": Vector2i(32, 232),
	"front_coast": Vector2i(48, 232),
	"front_desert": Vector2i(64, 232),
	"front_volcano": Vector2i(80, 232),
	"front_mountain": Vector2i(96, 232),
	"front_lakes": Vector2i(112, 232),
	"front_snow": Vector2i(128, 232),
	"decor_flower_r": Vector2i(144, 232),
	"decor_flower_y": Vector2i(160, 232),
	"decor_flower_w": Vector2i(176, 232),
	"decor_flower_b": Vector2i(192, 232),
	"decor_pebbles": Vector2i(208, 232),
	"decor_mushroom": Vector2i(224, 232),
	"decor_shell": Vector2i(240, 232),
	"decor_dry_bush": Vector2i(256, 232),
	"decor_ember": Vector2i(272, 232),
	"decor_lily": Vector2i(288, 232),
	"decor_snow_tuft": Vector2i(304, 232),
	"decor_bones": Vector2i(320, 232),
	"bridge_h": Vector2i(336, 232),
	"bridge_v": Vector2i(352, 232),
}
