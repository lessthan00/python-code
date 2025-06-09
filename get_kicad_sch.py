# 批量从kicad_sch的文件夹转化为原理图块形式.
import os
import json
import shutil
from pathlib import Path

def process_kicad_blocks(directory):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        # 跳过子目录和非.kicad_sch文件
        if not os.path.isfile(filepath) or not filename.endswith('.kicad_sch'):
            continue
            
        # 提取前缀
        prefix = filename[:-len('.kicad_sch')]
        
        # 创建目标文件夹
        folder_name = f"{prefix}.kicad_block"
        folder_path = os.path.join(directory, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # 移动文件到目标文件夹
        new_filepath = os.path.join(folder_path, filename)
        shutil.move(filepath, new_filepath)
        
        # 创建JSON文件
        json_filename = f"{prefix}.json"
        json_path = os.path.join(folder_path, json_filename)
        
        json_content = {
            "description": "描述",
            "keywords": "project",
            "fields": {
                "filename": rf"{filename}",
                "reliability": "20%"
            }
        }
        
        # 写入JSON文件，确保格式正确
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    target_dir = r"d:\Users\Desktop\my_sch"
    process_kicad_blocks(target_dir)
