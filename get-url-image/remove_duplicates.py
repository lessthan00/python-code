import pandas as pd
import os

def remove_duplicates(input_filename):
    # 读取CSV文件
    # 假设CSV文件的第一列是Image_URL
    df = pd.read_csv(input_filename)

    # 去重操作，基于Image_URL列
    df.drop_duplicates(subset=['Image_URL'], keep='first', inplace=True)

    # 生成新的文件名
    # 使用os.path.splitext来分割文件名和扩展名
    base_name, ext = os.path.splitext(input_filename)
    output_filename = f"{base_name}-new{ext}"

    # 将去重后的数据写入新的CSV文件
    df.to_csv(output_filename, index=False)

    print(f"去重后的文件已保存为: {output_filename}")

if __name__ == "__main__":
    # 输入CSV文件名
    input_filename = input("请输入CSV文件名: ")

    # 检查文件是否存在
    if os.path.exists(input_filename):
        remove_duplicates(input_filename)
    else:
        print(f"文件 {input_filename} 不存在，请检查文件名是否正确。")