import os
import re
import chardet

# 获取当前目录下所有 .txt 文件
txt_files = [f for f in os.listdir() if f.endswith(".txt")]

# 用于统计汉字和标点符号的字数
total_characters = 0

# 汉字和标点符号的正则表达式
pattern = re.compile(r'[\u4e00-\u9fa5\uff00-\uffef]')

# 遍历所有 .txt 文件并统计字数
for file in txt_files:
    try:
        # 检测文件编码
        with open(file, "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            file_encoding = result['encoding']

        # 以检测到的编码打开文件
        with open(file, "r", encoding=file_encoding) as f:
            content = f.read()
            # 找到所有汉字和标点符号
            characters = pattern.findall(content)
            total_characters += len(characters)
    except UnicodeDecodeError:
        print(f"无法解码文件: {file}")
    
# 输出总字数
print(f"当前目录下所有.txt文件的汉字和标点符号的总字数为：{total_characters}")
