#!/usr/bin/env python3
"""
WebGAL 资源 WebP 优化工具
- 交互式 CLI
- 多线程加速
- 自动更新场景文件中的引用
"""

import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


# 配置
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
WEBP_QUALITY = 80
MAX_WORKERS = 8

# 需要跳过的目录
SKIP_DIRS = {'figure'}

# 禁止转换的文件名模式
FORBIDDEN_PATTERNS = [
    re.compile(r'^texture_\d+'),  # texture_00.png, texture_01.png 等
]

# 场景命令（只处理 changeBg 和 changeFigure）
SCENE_COMMANDS = ['changeBg:', 'changeFigure:']


class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'


def c(text, color):
    return f"{color}{text}{Colors.RESET}" if sys.stdout.isatty() else text


def progress_bar(current: int, total: int, width: int = 30) -> str:
    """生成进度条字符串"""
    filled = int(width * current / total) if total > 0 else 0
    bar = '=' * filled + '-' * (width - filled)
    percent = int(100 * current / total) if total > 0 else 0
    return f'[{bar}] {percent}% ({current}/{total})'


def is_live2d_dir(path: Path) -> bool:
    """检查目录是否包含 Live2D 模型文件"""
    live2d_markers = ['*.model.json', '*.model3.json', '*.moc']
    for marker in live2d_markers:
        if any(path.glob(marker)):
            return True
    return False


def is_live2d_texture(file_path: Path) -> tuple[bool, str]:
    """检查文件是否在 Live2D 模型目录下"""
    for parent in file_path.parents:
        if is_live2d_dir(parent):
            return True, str(parent)
    return False, ''


def is_forbidden_filename(filename: str) -> bool:
    """检查文件名是否在禁止列表中"""
    name = Path(filename).stem
    return any(pattern.match(name) for pattern in FORBIDDEN_PATTERNS)


def should_skip_file(file_path: Path, skip_figure: bool) -> tuple[bool, str]:
    """检查文件是否应该跳过"""
    if is_forbidden_filename(file_path.name):
        return True, '禁止转换的文件名'

    is_live2d, live2d_dir = is_live2d_texture(file_path)
    if is_live2d:
        return True, 'Live2D 模型目录'

    parts = file_path.parts
    for part in parts:
        if part in SKIP_DIRS:
            if skip_figure and part == 'figure':
                return True, 'figure 目录已跳过'

    return False, ''


def convert_to_webp(input_path: Path, quality: int = WEBP_QUALITY) -> tuple[Path, bool, str]:
    """使用 ffmpeg 将图片转换为 WebP"""
    output_path = input_path.with_suffix('.webp')

    if output_path.exists():
        return input_path, None, '已存在'

    try:
        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-c:v', 'libwebp',
            '-quality', str(quality),
            str(output_path),
            '-y', '-loglevel', 'error'
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return input_path, True, '成功'
    except subprocess.CalledProcessError:
        return input_path, False, '失败'


def find_images(game_dir: Path) -> list[Path]:
    """递归查找所有图片文件"""
    images = []
    for ext in IMAGE_EXTENSIONS:
        images.extend(game_dir.rglob(f'*{ext}'))
    return sorted(images)


def update_scene_references(game_dir: Path) -> dict:
    """更新 scene 目录下的场景文件中的图片引用（递归）"""
    stats = {'updated': 0, 'checked': 0}

    scene_dir = game_dir / 'scene'
    if not scene_dir.is_dir():
        return stats

    for txt_file in scene_dir.rglob('*.txt'):
        stats['checked'] += 1
        content = txt_file.read_text(encoding='utf-8')
        original = content

        for cmd in SCENE_COMMANDS:
            pattern = rf'({re.escape(cmd)})\s*([^\s\-\;]+?)(\.png|\.jpg|\.jpeg)(?=[\s\)\]"\']|$)'
            content = re.sub(pattern, lambda m: f"{m.group(1)}{m.group(2)}.webp", content)

        if content != original:
            txt_file.write_text(content, encoding='utf-8')
            stats['updated'] += 1

    return stats


def interactive_yes_no(prompt: str, default: bool = False) -> bool:
    """交互式是/否选择"""
    suffix = ' [Y/n]: ' if default else ' [y/N]: '
    while True:
        response = input(c(prompt + suffix, Colors.CYAN)).strip().lower()
        if not response:
            return default
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        print(c('请输入 y 或 n', Colors.YELLOW))


def interactive_number(prompt: str, default: int, min_val: int = 1, max_val: int = 32) -> int:
    """交互式数字输入"""
    while True:
        response = input(c(f'{prompt} (直接回车默认 {default}): ', Colors.CYAN)).strip()
        if not response:
            return default
        try:
            value = int(response)
            if min_val <= value <= max_val:
                return value
            print(c(f'请输入 {min_val}-{max_val} 之间的数字', Colors.YELLOW))
        except ValueError:
            print(c('请输入有效的数字', Colors.YELLOW))


def interactive_choice(prompt: str, options: list[str], default: int = 0) -> str:
    """交互式选择"""
    print(c(f'\n{prompt}', Colors.CYAN))
    for i, opt in enumerate(options, 1):
        marker = ' *' if i - 1 == default else ''
        print(f'  {i}. {opt}{marker}')
    print()

    while True:
        response = input(c('请选择 (直接回车使用默认): ', Colors.CYAN)).strip()
        if not response:
            return options[default]
        try:
            idx = int(response) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print(c('无效选择', Colors.YELLOW))


def main():
    print(c('=' * 50, Colors.CYAN))
    print(c('WebGAL 资源 WebP 优化工具', Colors.CYAN))
    print(c('=' * 50, Colors.CYAN))

    # 1. 选择游戏目录
    print()
    game_path = input(c('请输入游戏目录路径: ', Colors.CYAN)).strip()
    if not game_path:
        print(c('[取消]', Colors.YELLOW))
        return

    game_path = Path(game_path) if Path(game_path).is_absolute() else Path.cwd() / game_path
    game_dir = game_path / 'game'

    if not game_path.exists():
        print(c(f'[错误] 目录不存在: {game_path}', Colors.RED))
        return

    if not game_dir.exists():
        print(c('[错误] 目录结构不正确，缺少 game 子目录', Colors.RED))
        return

    print(f'游戏目录: {game_path}')

    # 2. 选择模式
    mode = interactive_choice(
        '请选择操作模式',
        ['转换图片并更新引用', '仅更新引用（不转换图片）'],
        default=0
    )
    convert_mode = (mode == '转换图片并更新引用')

    # 3. 选择设置
    print()

    skip_figure = interactive_yes_no('是否跳过 figure 目录', default=False)

    if convert_mode:
        # 检查 ffmpeg
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(c('[错误] 未检测到 FFmpeg，请先安装', Colors.RED))
            return

        quality = interactive_number('图片质量 (1-100)', default=80, min_val=1, max_val=100)
        workers = interactive_number('并行线程数', default=8, min_val=1, max_val=32)
    else:
        quality = 80
        workers = 1

    print()

    # 4. 扫描文件
    print(c('[1/3] 扫描图片文件...', Colors.BLUE))
    all_images = find_images(game_dir)
    print(f'找到 {len(all_images)} 个图片文件')

    to_convert = []
    to_skip = []
    for img in all_images:
        skip, reason = should_skip_file(img, skip_figure)
        if skip:
            to_skip.append((img, reason))
        else:
            webp = img.with_suffix('.webp')
            if webp.exists():
                to_skip.append((img, '已转换'))
            else:
                to_convert.append(img)

    print(f'将转换 {len(to_convert)} 个文件，跳过 {len(to_skip)} 个')

    if to_skip:
        show_skip = input(c('是否显示跳过的文件? (y/N): ', Colors.CYAN)).strip().lower()
        if show_skip == 'y':
            for img, reason in to_skip:
                rel = img.relative_to(game_path)
                print(f'  {c("跳过", Colors.YELLOW)} {rel} ({reason})')

    print()

    if convert_mode:
        # 5. 确认转换
        print(c('[2/3] 转换图片为 WebP', Colors.BLUE))
        print(f'质量: {quality}, 线程: {workers}')

        if not interactive_yes_no('是否开始转换', default=True):
            print(c('[取消]', Colors.YELLOW))
            return

        print()

        converted = 0
        failed = 0
        completed = 0
        total = len(to_convert)

        if total == 0:
            print('没有文件需要转换')
        else:
            print(c(progress_bar(0, total), Colors.CYAN))

            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(convert_to_webp, img, quality): img for img in to_convert}

                for future in as_completed(futures):
                    completed += 1
                    img, result, msg = future.result()
                    if result is None:
                        pass
                    elif result:
                        converted += 1
                    else:
                        failed += 1

                    bar = progress_bar(completed, total)
                    print(f'\r{c(bar, Colors.CYAN)}', end='', flush=True)

            print()

        print()
        print(f'转换完成: {c(str(converted), Colors.GREEN)} 成功, {c(str(failed), Colors.RED)} 失败')

        # 6. 更新场景文件
        print()
        print(c('[3/3] 更新场景文件引用...', Colors.BLUE))
    else:
        # 仅更新引用模式
        print(c('[2/3] 更新场景文件引用...', Colors.BLUE))

    scene_dir = game_dir / 'scene'
    if not scene_dir.is_dir():
        print(c('  未找到 scene 目录，跳过', Colors.YELLOW))
    else:
        stats = update_scene_references(game_dir)
        print(f'  检查了 {stats["checked"]} 个场景文件')
        if stats['updated'] > 0:
            print(c(f'  更新了 {stats["updated"]} 个文件', Colors.GREEN))
        else:
            print('  无需更新')

    if convert_mode:
        # 7. 删除原图
        print()
        if interactive_yes_no('是否删除原图', default=False):
            deleted = 0
            for img in to_convert:
                webp = img.with_suffix('.webp')
                if webp.exists():
                    try:
                        img.unlink()
                        deleted += 1
                    except OSError:
                        pass
            print(f'已删除 {deleted} 个原文件')

    print()
    print(c('=' * 50, Colors.CYAN))
    print(c('处理完成！', Colors.GREEN))
    print(c('=' * 50, Colors.CYAN))


if __name__ == '__main__':
    main()
