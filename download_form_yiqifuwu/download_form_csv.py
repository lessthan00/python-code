import os
import csv
import re
import argparse
import time
import requests
from urllib.parse import urljoin
from fake_useragent import UserAgent

def sanitize_filename(filename):
    # 替换或移除非法字符（Windows和Unix都适用的通用方案）
    # 这里我们保留字母、数字、中文、下划线、连字符和点，其他替换为下划线
    # 你可以根据需要调整这个正则表达式
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def download_pdfs_from_csv(csv_path, output_folder=None):
    """
    从CSV文件下载PDF文件
    
    参数:
        csv_path (str): CSV文件路径
        output_folder (str): 输出文件夹路径，如果不指定则使用CSV文件名
    """
    # 设置输出文件夹
    if output_folder is None:
        output_folder = os.path.splitext(os.path.basename(csv_path))[0]
    
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)
    
    # 初始化失败记录
    failed_downloads = []
    
    # 读取CSV文件
    with open(csv_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            if row['status'].lower() != 'success':
                continue
                
            pdf_url = row['viewer_url']
            # 先去除首尾空白，再过滤非法字符
            raw_title = row['title'].strip()
            title = sanitize_filename(raw_title) + '.pdf'
            save_path = os.path.join(output_folder, title)
            
            # 如果文件已存在，跳过
            if os.path.exists(save_path):
                print(f"文件已存在，跳过: {title}")
                continue
                
            print(f"正在下载: {title}")
            
            try:
                # 处理相对URL
                if not pdf_url.startswith(('http://', 'https://')):
                    base_url = '/'.join(row['page_url'].split('/')[:3])
                    pdf_url = urljoin(base_url, pdf_url)
                
                # 下载PDF
                headers = {
                    'User-Agent': UserAgent().random,
                    'Referer': row['page_url'],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                    'Connection': 'keep-alive',
                }
                
                # 添加延迟防止被封
                time.sleep(2)
                
                response = requests.get(
                    pdf_url,
                    headers=headers,
                    stream=True,
                    timeout=30
                )
                
                # 检查响应状态
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    print(f"下载成功: {title}")
                else:
                    raise Exception(f"HTTP状态码: {response.status_code}")
                    
            except Exception as e:
                print(f"下载失败: {title} - 错误: {str(e)}")
                failed_downloads.append({
                    'title': title,
                    'url': pdf_url,
                    'error': str(e)
                })
    
    # 保存失败记录
    if failed_downloads:
        failed_csv_path = os.path.join(output_folder, 'failed_downloads.csv')
        with open(failed_csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'url', 'error'])
            writer.writeheader()
            writer.writerows(failed_downloads)
        print(f"\n部分文件下载失败，详情见: {failed_csv_path}")
    else:
        print("\n所有文件下载完成！")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download PDFs from CSV file')
    parser.add_argument('csv_file', help='Path to the CSV file')
    args = parser.parse_args()
    
    download_pdfs_from_csv(args.csv_file)