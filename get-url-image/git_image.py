import csv
import os
import requests

def download_images_from_csv(csv_filename):
    # 获取CSV文件所在的目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, csv_filename)
    
    # 创建与CSV文件同名的文件夹
    folder_name = os.path.splitext(csv_filename)[0]
    save_dir = os.path.join(base_dir, folder_name)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 设置请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # 读取CSV文件并下载图片
    with open(csv_path, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # 跳过标题行
        for row in csv_reader:
            for url in row:
                url = url.strip()  # 去除URL两端的空白字符
                if not url.startswith(('http://', 'https://')):
                    print(f"Skipping invalid URL: {url}")
                    continue
                
                try:
                    # 获取图片文件名
                    image_name = os.path.basename(url).split('?')[0]
                    image_path = os.path.join(save_dir, image_name)
                    
                    # 下载图片
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        with open(image_path, 'wb') as image_file:
                            image_file.write(response.content)
                        print(f"Downloaded: {image_name}")
                    else:
                        print(f"Failed to download: {url} (Status Code: {response.status_code})")
                except Exception as e:
                    print(f"Error downloading {url}: {e}")

if __name__ == "__main__":
    csv_filename = input("Enter the CSV filename: ")
    download_images_from_csv(csv_filename)