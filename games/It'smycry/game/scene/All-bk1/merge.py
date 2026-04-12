import os
import re
from collections import defaultdict

# 获取当前目录下所有 .txt 文件
txt_files = [f for f in os.listdir() if f.endswith(".txt")]

# 用于存储不同 CxxSyy 分组的内容
grouped_files = defaultdict(list)

# 匹配 CxxSyy_Scenezz.txt 格式
pattern = re.compile(r"^(C\d{2}S\d{2})_(Scene\d{2})\.txt$")

# 遍历所有 .txt 文件，按 CxxSyy 分组
for file in txt_files:
    match = pattern.match(file)
    if match:
        group_key = match.group(1)  # CxxSyy
        scene_name = match.group(2)  # Scenezz
        grouped_files[group_key].append((scene_name, file))

# 遍历分组并写入新的合并文件
for group, scenes in grouped_files.items():
    output_file = f"{group}.txt"  # 目标合并文件名，如 C01S01.txt
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        for scene_name, file in sorted(scenes):  # 按 Scene 排序
            outfile.write(f"### {group}_{scene_name} ###\n\n")  # 标题
            with open(file, "r", encoding="utf-8") as infile:
                outfile.write(infile.read() + "\n\n")  # 读取并写入内容

print("✅ 合并完成！")
