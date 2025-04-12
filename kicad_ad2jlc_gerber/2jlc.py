import os
import shutil
import json
import zipfile
import datetime
from pathlib import Path
import sys

def get_resource_path(relative_path):
    """ 获取资源文件的绝对路径（无论是否打包） """
    if getattr(sys, 'frozen', False):
        # 打包后，资源文件在临时目录中
        base_path = sys._MEIPASS
    else:
        # 开发时，资源文件在脚本所在目录中
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

# 相对地址(不会变的)在exe内部
GERBER_JSON = get_resource_path("GerberX2.json")

def get_exe_dir():
    """ 获取exe所在目录（无论是否打包） """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent  # 打包后获取exe所在目录
    else:
        return Path(__file__).parent  # 开发时获取脚本所在目录

# 会改变的地址,在exe外部
BASE_PATH = get_exe_dir()

# 构建路径
PATH_FINAL = os.path.join(BASE_PATH, r'jlc_gerber')
gerber_folder = os.path.join(BASE_PATH, r"gerber")
timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
# zip_path = os.path.join(os.path.dirname(BASE_PATH), f"out_{BASE_PATH.name}-{timestamp}.zip")
zip_path = os.path.join(BASE_PATH, f"out_{BASE_PATH.name}-{timestamp}.zip")

def create_folder(path):
    """创建目标文件夹（如果不存在）"""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"Folder '{path}' ready")

def clean_folder(path):
    """清空目标文件夹"""
    if not os.path.exists(path):
        return
    for item in Path(path).iterdir():
        if item.is_file():
            item.unlink()
        else:
            shutil.rmtree(item)
    print(f"Folder '{path}' cleaned")

def load_json_data(file_path):
    """
    读取 JSON 文件并返回数据。

    :param file_path: JSON 文件的路径
    :return: 字典形式的数据
    """
    with open(file_path, mode='r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def move_and_rename_files(source_path, destination_path, old_name, new_name):
    """移动并重命名文件"""
    source_file = os.path.join(source_path, old_name)
    destination_file = os.path.join(destination_path, new_name)
    shutil.copy(source_file, destination_file)
    print(f"Moved and renamed: {old_name} -> {new_name}")

def add_file_header(file_path, header_lines):
    """向文件添加头部信息"""
    # 读取原有内容
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # 构建新内容
    new_content = "\n".join(header_lines) + "\n" + original_content

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Header added to: {file_path}")

def zip_folder(folder_path, output_path):
    """打包文件夹为ZIP"""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
    print(f"ZIP created: {output_path}")

def main():
    # 初始化目标文件夹
    create_folder(PATH_FINAL)
    clean_folder(PATH_FINAL)

    # 加载 JSON 配置
    json_data = load_json_data(GERBER_JSON)

    # 遍历 JSON 数据
    for layer, config in json_data.items():
        jlc_filename = config.get("jlc_filename")
        if not jlc_filename:  # 如果 jlc_filename 为 None，跳过
            continue

        # 遍历 gerber 文件夹中的文件
        for file_name in os.listdir(gerber_folder):
            # 检查文件名是否包含某个键值（除去 jlc_filename 和 jlc_header）
            try:
                if any(
                    isinstance(value, str) and value in file_name  # 确保 value 是字符串
                    for key, value in config.items()
                    if key not in ["jlc_filename", "jlc_header"]
                ):
                    # 移动并重命名文件
                    move_and_rename_files(gerber_folder, PATH_FINAL, file_name, jlc_filename)

                    # 在文件开头插入头部信息
                    file_new_path = os.path.join(PATH_FINAL, jlc_filename)
                    if os.path.exists(file_new_path):
                        add_file_header(file_new_path, config["jlc_header"])
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

    # 打包文件
    zip_folder(PATH_FINAL, zip_path)

if __name__ == "__main__":
    main()
