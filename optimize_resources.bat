@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ==================================================
echo         WebGAL 资源 WebP 优化工具
echo ==================================================

set "game_folder=MJKNMZ"
set /p game_folder="请输入游戏文件夹名称 (直接回车默认: !game_folder!): "

set "TARGET_DIR=games\%game_folder%"

if not exist "%TARGET_DIR%" (
    echo [错误] 找不到目录: %TARGET_DIR%
    pause
    exit /b
)

if not exist "%TARGET_DIR%\game" (
    echo [错误] 目录结构不正确，缺少 game 子目录
    pause
    exit /b
)

set "skip_figure=n"
set /p skip_figure="是否跳过 figure 目录 (y/n, 默认 n): "

:: 是否并行转换（多线程）
set "parallel=n"
set /p parallel="是否开启多线程加速 (y/n, 默认 n): "

ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 FFmpeg
    pause
    exit /b
)

echo.
echo [1/3] 正在转换图片为 WebP...
echo.

set "converted=0"
set "skipped=0"
set "failed=0"

set "GAME_DIR=%TARGET_DIR%\game"

if /i "%parallel%"=="y" (
    :: 并行模式：收集文件后批量处理
    set "file_list="

    for /r "%GAME_DIR%" %%f in (*.png) do call :collect_file "%%f"
    for /r "%GAME_DIR%" %%f in (*.jpg) do call :collect_file "%%f"
    for /r "%GAME_DIR%" %%f in (*.jpeg) do call :collect_file "%%f"

    :: 使用 PowerShell 并行转换
    powershell -NoProfile -ExecutionPolicy Bypass -Command "
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        $files = @(%file_list%)
        $jobs = @()
        foreach ($f in $files) {
            $dest = [System.IO.Path]::ChangeExtension($f, '.webp')
            if (-not (Test-Path $dest)) {
                $jobs += Start-Process -FilePath 'ffmpeg' -ArgumentList '-i', \"`\"$f`\"\", '-c:v', 'libwebp', '-quality', '80', \"`"$dest`"\" -y -loglevel error -PassThru
            }
        }
        $jobs | Wait-Process
        Write-Host ('已启动 ' + $jobs.Count + ' 个转换任务')
    "
) else (
    :: 串行模式
    for /r "%GAME_DIR%" %%f in (*.png) do call :convert_file "%%f"
    for /r "%GAME_DIR%" %%f in (*.jpg) do call :convert_file "%%f"
    for /r "%GAME_DIR%" %%f in (*.jpeg) do call :convert_file "%%f"
)

echo.
echo 转换统计: 成功 !converted!, 跳过 !skipped!, 失败 !failed!

echo.
echo [2/3] 正在更新场景文件中的引用...

powershell -NoProfile -ExecutionPolicy Bypass -Command "
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$targetDir = '%TARGET_DIR%\game'

@('scene', 'sce') | ForEach-Object {
    $sceneDir = Join-Path $targetDir $_
    if (Test-Path $sceneDir) {
        Get-ChildItem -Path $sceneDir -Filter *.txt | ForEach-Object {
            $content = Get-Content $_.FullName -Raw -Encoding UTF8
            $original = $content

            :: 只替换 changeBg: 和 changeFigure: 命令中的图片引用
            $content = $content -replace '(changeBg:|changeFigure:)\s*([^\s\-\;]+?)(\.png|\.jpg|\.jpeg)(?=[\s\)\]''\"]|$)', '$1$2.webp'

            if ($content -ne $original) {
                Write-Host ('  更新: ' + $_.Name)
                Set-Content $_.FullName $content -Encoding UTF8
            }
        }
    }
}
Write-Host '  场景文件更新完成'
"

echo.
echo [3/3] 清理工作...
set "delete_old=n"
set /p delete_old="是否删除已转换的原图? (y/n, 默认 n): "

if /i "!delete_old!"=="y" (
    set "deleted=0"
    for /r "%GAME_DIR%" %%f in (*.png) do call :delete_if_converted "%%f"
    for /r "%GAME_DIR%" %%f in (*.jpg) do call :delete_if_converted "%%f"
    for /r "%GAME_DIR%" %%f in (*.jpeg) do call :delete_if_converted "%%f"
    echo 已删除 !deleted! 个原文件。
)

echo.
echo ==================================================
echo             处理完成！
echo ==================================================
pause
exit /b

:collect_file
set "current_file=%~1"

call :should_skip "%current_file%"
if errorlevel 1 exit /b

if defined file_list (
    set "file_list=!file_list!,'%current_file%'"
) else (
    set "file_list='%current_file%'"
)
exit /b

:should_skip
set "current_file=%~1"

for %%P in ("%current_file%") do set "file_dir=%%~dpP"

:: figure 目录检查
echo %file_dir% | findstr /i "\\figure\\" >nul
if !errorlevel! equ 0 (
    if "!skip_figure!"=="y" (
        set /a skipped+=1
        exit /b 1
    )
)

:: Live2D .model.json 检查
if exist "%file_dir%*.model.json" (
    set /a skipped+=1
    exit /b 1
)

:: texture_*.png 模式检查
for %%F in ("%~n1") do set "basename=%%~nF"
echo !basename! | findstr /i "^texture_[0-9]" >nul
if !errorlevel! equ 0 (
    set /a skipped+=1
    exit /b 1
)

:: 目标文件已存在检查
set "dest=%~dpn1.webp"
if exist "!dest!" (
    set /a skipped+=1
    exit /b 1
)

exit /b 0

:convert_file
set "current_file=%~1"

call :should_skip "%current_file%"
if errorlevel 1 exit /b

ffmpeg -i "!current_file!" -c:v libwebp -quality 80 "!dest!" -y -loglevel error
if errorlevel 1 (
    echo   [失败] %~nx1
    set /a failed+=1
) else (
    echo   [OK] %~nx1
    set /a converted+=1
)
exit /b

:delete_if_converted
set "dest=%~dpn1.webp"

echo %~1 | findstr /i "\\figure\\" >nul
set "in_figure=!errorlevel!

for %%P in ("%~dp1") do set "par_dir=%%~dpP"
if exist "!par_dir!*.model.json" exit /b

for %%F in ("%~n1") do set "basename=%%~nF"
echo !basename! | findstr /i "^texture_[0-9]" >nul
if !errorlevel! equ 0 exit /b

set "do_del=1"
if "!skip_figure!"=="y" if "!in_figure!"=="0" set "do_del=0"

if "!do_del!"=="1" if exist "!dest!" (
    del "%~1"
    set /a deleted+=1
)
exit /b
