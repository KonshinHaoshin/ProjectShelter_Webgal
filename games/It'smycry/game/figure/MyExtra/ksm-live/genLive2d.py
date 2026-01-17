import os
import json
import shutil


def list_files_in_directory(directory):
    """
    列出指定目录中的所有文件名。
    :param directory: 要扫描的目录。
    :return: 文件名列表。
    """
    try:
        files = os.listdir(directory)
        return files
    except Exception as e:
        print(f"无法读取目录: {e}")
        return []


def generate_json_from_files(files, character_name, output_path):
    """
    根据文件名数组生成 JSON 文件，格式参考 model.json。
    :param files: 文件名列表。
    :param character_name: 角色名，用于生成路径。
    :param output_path: 输出 JSON 文件路径。
    """
    # 初始化 JSON 结构
    json_data = {
        "version": "Sample 1.0.0",
        "model": f"live2d/chara/{character_name}.moc",
        "physics": f"live2d/chara/{character_name}.physics.json",
        "textures": [
            f"live2d/chara/texture_00.png",
            f"live2d/chara/texture_01.png",
        ],
        "motions": {},
        "expressions": []
    }

    # 分类文件
    for file in files:
        if file.endswith(".mtn"):  # 动作文件
            motion_name = os.path.splitext(file)[0]
            json_data["motions"].setdefault(motion_name, []).append({
                "file": f"live2d/chara/{file}"
            })
        elif file.endswith(".exp.json"):  # 表情文件
            expression_name = os.path.splitext(file)[0]
            json_data["expressions"].append({
                "name": expression_name,
                "file": f"live2d/chara/{file}"
            })

    # 输出 JSON 文件
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"JSON 文件已生成：{output_path}")
    except Exception as e:
        print(f"无法生成 JSON 文件: {e}")


def move_files_to_subdirectory(source_directory, target_directory):
    """
    将文件从 source_directory 移动到 target_directory。
    :param source_directory: 源目录。
    :param target_directory: 目标子目录。
    """
    try:
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        files = os.listdir(source_directory)
        for file in files:
            source_path = os.path.join(source_directory, file)
            target_path = os.path.join(target_directory, file)
            shutil.move(source_path, target_path)

        print(f"所有文件已移动到 {target_directory}")
    except Exception as e:
        print(f"文件移动失败: {e}")


if __name__ == "__main__":
    # 当前脚本目录
    script_directory = os.path.dirname(os.path.abspath(__file__))
    raw_files_directory = os.path.join(script_directory, "rawFiles")
    target_directory = os.path.join(script_directory, "live2d/chara")

    # 获取文件列表
    file_list = list_files_in_directory(raw_files_directory)

    # 生成 JSON 文件
    character_name = "ririko_casual"  # 替换为你的角色名
    json_output_path = os.path.join(script_directory, f"model.json")
    generate_json_from_files(file_list, character_name, json_output_path)

    # 移动文件
    move_files_to_subdirectory(raw_files_directory, target_directory)
