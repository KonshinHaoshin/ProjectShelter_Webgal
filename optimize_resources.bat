@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ==================================================
echo         庇护所 WebGAL 资源一键 WebP 优化工具 
echo ==================================================

:: 1. 获取目标文件夹
set /p game_folder="请输入要处理的游戏文件夹名称 (位于 games 目录下, 例如 manosaba1.2): "

set "TARGET_DIR=games\%game_folder%"

if not exist "%TARGET_DIR%" (
    echo [错误] 找不到目录: %TARGET_DIR%
    pause
    exit /b
)

:: 2. 检查 FFmpeg 是否安装
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 FFmpeg，请先安装 FFmpeg 并将其添加到系统环境变量 PATH 中。
    pause
    exit /b
)

echo.
echo [1/3] 正在使用 FFmpeg 递归转换图片为 WebP...
:: 递归寻找 png, jpg, jpeg 并转换
for /r "%TARGET_DIR%" %%f in (*.png *.jpg *.jpeg) do (
    set "src=%%f"
    set "dest=%%~dpnf.webp"
    if not exist "!dest!" (
        echo 正在转换: %%~nxf
        ffmpeg -i "%%f" -c:v libwebp -lossless 0 -compression_level 6 -quality 80 "!dest!" -y -loglevel error
    )
)

echo.
echo [2/3] 正在更新代码和配置中的引用 (.png/.jpg -> .webp)...
:: 使用 PowerShell 进行批量文本替换
echo 正在处理 JS 文件和场景配置...

powershell -Command "$targetDir = '%TARGET_DIR%'; $files = Get-ChildItem -Path \"$targetDir\assets\*.js\", \"$targetDir\game\Item\*\", \"$targetDir\game\scene\*\", \"games.json\" -ErrorAction SilentlyContinue; foreach ($f in $files) { if (-not $f.PSIsContainer) { echo ('正在更新引用: ' + $f.FullName); $content = Get-Content $f.FullName -Raw -Encoding UTF8; $content = $content -replace '\.png(?=[\"''\s\)])', '.webp' -replace '\.jpg(?=[\"''\s\)])', '.webp' -replace '\.jpeg(?=[\"''\s\)])', '.webp'; Set-Content $f.FullName $content -Encoding UTF8 } }"

echo.
echo [3/3] 清理工作...
echo 注意：建议在确认游戏运行正常后再删除原图。
set /p delete_old="是否现在删除原始的 png/jpg/jpeg 文件? (y/n): "
if /i "%delete_old%"=="y" (
    for /r "%TARGET_DIR%" %%f in (*.png *.jpg *.jpeg) do (
        del "%%f"
    )
    echo 已清理原始图片文件。
)

echo.
echo ==================================================
echo             处理完成！
echo             1. 已转换所有图片为 webp
echo             2. 已更新 JS、Item、Scene 及 games.json 中的引用
echo ==================================================
pause

