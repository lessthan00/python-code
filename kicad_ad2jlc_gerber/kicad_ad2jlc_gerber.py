import os
import shutil
import csv
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
GERBER_CSV = get_resource_path("data/gerber.csv")
HEADER_FILE_MAP = {
    "hear1": get_resource_path("data/jlc_gerber_header.md"),
    "hear2": get_resource_path("data/jlc_gerber_header2.md")
}

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
ad_gerber_floder = os.path.join(BASE_PATH, r"ad_gerber")
kicad_gerber_floder = os.path.join(BASE_PATH, r"kicad_gerber")
timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
zip_path = os.path.join(BASE_PATH , f"out_{BASE_PATH.name}-{timestamp}.zip")

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

def load_csv_data(file_path):
    """
    读取带有表头的CSV文件，并返回所有数据。

    :param file_path: CSV文件的路径
    :return: 列表，每个元素是一行数据，数据以字典形式返回，键为表头
    """
    data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def copy_and_rename_files(source_path, file_name, file_new_name):
    """根据CSV配置复制并重命名文件"""
    source_file = os.path.join(source_path, file_name)

    destination_file = os.path.join(PATH_FINAL, file_new_name)

    shutil.copy(source_file, destination_file)

def add_file_header(file_path, row, csv_data):
    """向文件添加头部信息"""
    header_begin = row['jlc_begin']
    header_type = row['hear']

    # 修正
    if header_begin == ';TYPE=PLATED;Layer: NPTH_Through':
        header_begin = ';TYPE=PLATED\n;Layer: NPTH_Through'
    elif header_begin == ';TYPE=PLATED;Layer: PTH_Through':
        header_begin = ';TYPE=PLATED\n;Layer: PTH_Through'
    
    # 读取原有内容
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # 构建新内容
    new_content = []
    new_content.append(header_begin.strip())
    

    # 添加对应Header文件内容
    header_file = HEADER_FILE_MAP.get(header_type)
    if header_file and os.path.exists(header_file):
        with open(header_file, 'r', encoding='utf-8') as hf:
            new_content.append(hf.read().strip())
    
    new_content.append(original_content)
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_content))
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
    # 加载CSV配置
    csv_data = load_csv_data(GERBER_CSV)


    for row in csv_data:
        if os.path.isdir(ad_gerber_floder):
            source_path = ad_gerber_floder
            for file_name in os.listdir(source_path):
                if row['ad_gbr'] in file_name:
                    copy_and_rename_files(source_path, file_name,row['jlc_filename'])
                elif row['ad_filename'] in file_name:
                    copy_and_rename_files(source_path, file_name,row['jlc_filename'])
                else:
                    pass
        elif os.path.isdir(kicad_gerber_floder):
            source_path = kicad_gerber_floder
            for file_name in os.listdir(source_path):
                if row['kicad_gbr'] in file_name:
                    copy_and_rename_files(source_path, file_name,row['jlc_filename'])
                elif row['kicad_filename'] in file_name:
                    copy_and_rename_files(source_path, file_name,row['jlc_filename'])
                elif row['kicad_filename2'] in file_name:
                    copy_and_rename_files(source_path, file_name,row['jlc_filename'])
                else:
                    pass
        else:
            pass

    for row in csv_data:
        file_new_path = os.path.join(PATH_FINAL,row['jlc_filename']) 
        if os.path.exists(file_new_path):
            add_file_header(file_new_path, row, csv_data)

    # 打包文件
    zip_folder(PATH_FINAL, zip_path)

if __name__ == "__main__":
    main()