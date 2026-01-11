@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ==================================================
echo         庇护所 WebGAL 资源一键 WebP 优化工具 
echo ==================================================

:: 1. 获取目标文件夹
set "game_folder=MJKNMZ"
set /p game_folder="请输入游戏文件夹名称 (直接回车默认: !game_folder!): "

set "TARGET_DIR=games\%game_folder%"

if not exist "%TARGET_DIR%" (
    echo [错误] 找不到目录: %TARGET_DIR%
    pause
    exit /b
)

:: 2. 选择是否跳过 figure 目录
set "skip_figure=n"
set /p skip_figure="是否跳过 figure 目录 (立绘目录)? (y/n, 默认 n): "

:: 3. 检查 FFmpeg 是否安装
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 FFmpeg，请确认已安装。
    pause
    exit /b
)

echo.
echo [1/3] 正在转换图片为 WebP...
for /r "%TARGET_DIR%" %%f in (*.png *.jpg *.jpeg) do (
    set "current_file=%%f"
    set "process_this=1"
    
    rem 检查路径中是否包含 \figure\ (使用 rem 替代 ::)
    echo !current_file! | findstr /i "\\figure\\" >nul
    if !errorlevel! equ 0 (
        if "!skip_figure!"=="y" set "process_this=0"
    )
    
    if "!process_this!"=="1" (
        set "dest=%%~dpnf.webp"
        if not exist "!dest!" (
            echo 正在转换: %%~nxf
            ffmpeg -i "%%f" -c:v libwebp -lossless 0 -compression_level 6 -quality 80 "!dest!" -y -loglevel error
        )
    )
)

echo.
echo [2/3] 正在更新引用...
powershell -Command "$targetDir = '%TARGET_DIR%'; $files = Get-ChildItem -Path \"$targetDir\assets\*.js\", \"$targetDir\game\Item\*\", \"$targetDir\game\scene\*\", \"games.json\" -ErrorAction SilentlyContinue; foreach ($f in $files) { if (-not $f.PSIsContainer) { echo ('正在更新引用: ' + $f.FullName); $content = Get-Content $f.FullName -Raw -Encoding UTF8; if ($f.FullName -like '*\game\scene\*') { $content = $content -replace 'changeBg\s*:\s*([^,\r\n\s\"'']+\.png)', { $args[0].Value -replace '\.png', '.webp' } }; $content = $content -replace '\.png(?=[\"''\s\)])', '.webp' -replace '\.jpg(?=[\"''\s\)])', '.webp' -replace '\.jpeg(?=[\"''\s\)])', '.webp'; Set-Content $f.FullName $content -Encoding UTF8 } }"

echo.
echo [3/3] 清理工作...
set "delete_old=n"
set /p delete_old="是否删除已转换的原图? (y/n, 默认 n): "

if /i "!delete_old!"=="y" (
    for /r "%TARGET_DIR%" %%f in (*.png *.jpg *.jpeg) do (
        set "current_file=%%f"
        echo !current_file! | findstr /i "\\figure\\" >nul
        set "in_figure=!errorlevel!"
        
        set "do_del=1"
        if "!skip_figure!"=="y" if "!in_figure!"=="0" set "do_del=0"
        
        if "!do_del!"=="1" if exist "%%~dpnf.webp" (
            del "%%f"
        )
    )
    echo 已清理。
)

echo.
echo ==================================================
echo             处理完成！
echo ==================================================
pause