import csv
import json

# 定义CSV文件路径和输出JSON文件路径
csv_file_path = 'GerberX2.csv'  # 替换为你的CSV文件路径
json_file_path = 'GerberX2.json'  # 输出的JSON文件路径

# 读取CSV文件并转换为字典
def csv_to_json(csv_file, json_file):
    data = {}
    
    with open(csv_file, mode='r', encoding='utf-8') as file:
        # 使用csv.DictReader读取CSV文件
        reader = csv.DictReader(file)
        
        # 遍历每一行数据
        for row in reader:
            # 使用'name'列作为键
            key = row['name']
            
            # 过滤掉空值和其他不需要的列
            filtered_row = {
                k: v.strip() if v and v.strip() else None  # 如果值为空或仅有空格，则设置为None
                for k, v in row.items()
                if k != 'name'  # 排除'name'列
            }
            
            # 将过滤后的行添加到数据字典中
            data[key] = filtered_row
    
    # 将字典写入JSON文件
    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# 调用函数
csv_to_json(csv_file_path, json_file_path)

print(f"CSV文件已成功转换为JSON文件：{json_file_path}")