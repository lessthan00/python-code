import os
import csv
import re
import argparse
import time
import random
import requests
from urllib.parse import urljoin, urlparse, parse_qs

def sanitize_filename(filename):
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    filename = re.sub(r'[\/∕]', "_", filename)
    filename = re.sub(r'\s+', ' ', filename).strip()
    return filename

def validate_pdf(content):
    return content[:4] == b'%PDF'

def extract_real_pdf_url(viewer_url):
    """从查看器URL中提取真实的PDF URL"""
    parsed = urlparse(viewer_url)
    query = parse_qs(parsed.query)
    if 'file' in query:
        return urljoin(f"{parsed.scheme}://{parsed.netloc}", query['file'][0])
    return None

def download_pdfs_from_csv(csv_path, output_folder=None):
    if output_folder is None:
        output_folder = os.path.splitext(os.path.basename(csv_path))[0]  # 修正：使用basename而不是splename
    
    os.makedirs(output_folder, exist_ok=True)
    failed_downloads = []
    
    with open(csv_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            if 'status' not in row or row['status'].lower() != 'success':  # 添加检查status字段是否存在
                continue
                
            viewer_url = row['viewer_url']
            raw_title = row['title'].strip()
            title = sanitize_filename(raw_title) + '.pdf'
            save_path = os.path.join(output_folder, title)
            
            if os.path.exists(save_path):
                print(f"文件已存在，跳过: {title}")
                continue
                
            print(f"正在处理: {title}")
            
            try:
                # 提取真实PDF URL
                pdf_url = extract_real_pdf_url(viewer_url)
                if not pdf_url:
                    raise Exception("无法从查看器URL中提取PDF链接")
                
                # 更真实的浏览器头信息
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Referer': viewer_url,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                }
                
                # 添加必要的cookies
                cookies = {
                    '__51vcke__JhsImm1MEoeBpCnP': 'd9d1698f-0544-54d9-97ed-fd7607439670',
                    '__51vuft__JhsImm1MEoeBpCnP': str(int(time.time() * 1000)),
                    'Hm_lvt_7dd17b942bff8da009982725a8ea9474': '1743147609,1743148284',
                    '__51uvsct__JhsImm1MEoeBpCnP': '3'
                }
                
                time.sleep(3 + random.random() * 2)
                
                session = requests.Session()
                response = session.get(
                    pdf_url,
                    headers=headers,
                    cookies=cookies,
                    stream=True,
                    timeout=60
                )
                
                if response.status_code != 200:
                    raise Exception(f"HTTP状态码: {response.status_code}")
                
                content = response.content
                
                if not validate_pdf(content):
                    if b'<html' in content[:1024].lower():
                        raise Exception("服务器返回了HTML页面而非PDF文件")
                    raise Exception("下载的文件不是有效的PDF格式")
                
                with open(save_path, 'wb') as f:
                    f.write(content)
                    
                file_size = os.path.getsize(save_path)
                if file_size < 1024:
                    os.remove(save_path)
                    raise Exception(f"文件过小({file_size}字节)，可能是错误页面")
                
                print(f"下载成功: {title} ({file_size/1024:.1f} KB)")
                    
            except Exception as e:
                print(f"下载失败: {title} - 错误: {str(e)}")
                failed_downloads.append({
                    'title': raw_title,  # 使用原始标题而不是处理过的标题
                    'url': pdf_url if 'pdf_url' in locals() else viewer_url,
                    'error': str(e)
                })
    
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