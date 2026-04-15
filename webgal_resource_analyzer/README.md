# WebGAL 资源分析工具

用于分析 WebGAL 项目中哪些资源被使用、哪些未被使用，支持资源瘦身和优化。

## 工具列表

1. **resource_analyzer** - 资源分析工具（检测未使用资源）
2. **optimize_resources** - WebP 优化工具（图片格式转换）

---

# 1. 资源分析工具 (resource_analyzer)

## 安装

需要 Python 3.10+。

## 使用方法

```bash
# 分析单个游戏项目
python main.py /path/to/game

# 示例
python main.py games/MJKNMZ
python main.py ../MJKNMZ
```

### 输出格式

```bash
# 默认控制台输出（带颜色）
python main.py games/MJKNMZ

# 输出 JSON 报告
python main.py games/MJKNMZ -f json -o report.json

# 输出文本报告
python main.py games/MJKNMZ -f text -o report.txt
```

### 其他选项

```bash
# 禁用颜色输出
python main.py games/MJKNMZ --no-color

# 显示帮助
python main.py --help
```

## 输出说明

分析报告会显示：

- **Total resources**: 扫描到的资源文件总数
- **Used resources**: 在场景脚本中被引用的资源
- **Unused resources**: 未被引用的资源（可安全删除）
- **Missing references**: 引用了但找不到文件的资源（文件名可能有误）

## 支持的资源类型

| 命令 | 资源类型 | 目录 |
|------|----------|------|
| `bgm:` | BGM 音乐 | `game/bgm/` |
| `changeBg:` | 背景图 | `game/background/` |
| `changeFigure:` | 立绘 | `game/figure/` |
| `playEffect:` | 音效 | `game/vocal/` |
| `vocal/语音:` | 语音 | `game/vocal/` |
| `setAnimation:` | 动画 | `game/animation/` |

## 支持的文件扩展名

- 图片: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`
- 音频: `.mp3`, `.wav`, `.ogg`, `.flac`, `.aac`
- 视频: `.mp4`, `.webm`, `.avi`, `.mov`
- 动画: `.json`

---

# 2. WebP 优化工具 (optimize_resources)

将图片转换为 WebP 格式以节省空间，支持多线程加速。**交互式 CLI**，运行后按提示操作。

## 依赖

需要安装 FFmpeg（包含 libwebp 支持）。

## 使用方法

```bash
# 交互式运行
python optimize_resources.py
```

按提示依次输入：

```
请输入游戏目录路径: games/MJKNMZ
是否跳过 figure 目录 [y/N]: n
图片质量 (1-100) (直接回车默认 80): 80
并行线程数 (直接回车默认 8): 8

[1/3] 扫描图片文件...
找到 110 个图片文件
将转换 26 个文件，跳过 84 个
是否显示跳过的文件? (y/N): n

[2/3] 转换图片为 WebP
质量: 80, 线程: 8
是否开始转换 [Y/n]: y

[3/3] 更新场景文件引用...

是否删除原图 [y/N]: n
```

## 自动跳过的内容

以下文件和目录**不会**被转换：

1. **Live2D 贴图** - 包含 `.model.json`、`.model3.json` 或 `.moc` 文件的目录下的所有图片
2. **texture_*.png** - 形如 `texture_00.png`、`texture_01.png` 等 Live2D 贴图
3. **figure 目录** - 交互式询问是否跳过
4. **已存在的 WebP 文件** - 不重复转换

## 场景文件更新

转换后会自动更新场景文件中的引用，只处理 `changeBg:` 和 `changeFigure:` 命令。

例如场景文件中的：
```
changeBg:bg_001.png
changeFigure:eri_normal
```

会自动更新为：
```
changeBg:bg_001.webp
changeFigure:eri_normal.webp
```

## 完整示例

```bash
# 1. 先用 dry-run 模式查看将要转换的文件
python optimize_resources.py games/MJKNMZ --dry-run

# 2. 确认无误后执行转换（跳过 figure，质量 85，16 线程）
python optimize_resources.py games/MJKNMZ --skip-figure -q 85 -w 16

# 3. 转换完成后检查结果
python main.py games/MJKNMZ -f json -o report_after.json
```

## 注意事项

1. 转换前建议备份项目
2. 使用 `--dry-run` 先预览要转换的文件
3. Live2D 模型需要使用原始 PNG 格式，**不要**转换 Live2D 目录下的图片
4. 转换后的场景文件引用是自动更新的，但仍建议测试游戏运行正常
