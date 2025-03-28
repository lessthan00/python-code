import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin
import os

# 常量设置
BASE_URL = "https://www.yiqifuwu.com"
START_PAGE = 1
MAX_ERRORS = 30
REQUEST_DELAY = 1  # 请求间隔时间(秒)，防止被封
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
OUTPUT_FILE = 'yiqifuwu_pdf_viewer_urls.csv'

def get_pdf_viewer_url(page_num):
    """从标准页面获取PDF查看器URL和标题"""
    url = f"{BASE_URL}/standard/{page_num}.html"
    try:
        # 发送HTTP请求获取页面内容
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # 如果状态码不是200则抛出异常
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含PDF查看器的iframe标签
        iframe = soup.find('iframe', src=lambda x: x and 'viewer.html?file=' in x)
        
        # 获取页面标题并清理
        title = soup.title.string if soup.title else ""
        cleaned_title = title.replace("-宜器服务网", "").strip()
        
        if iframe:
            # 构建完整的URL
            viewer_path = iframe['src']
            full_viewer_url = urljoin(BASE_URL, viewer_path)
            return {
                'page_num': page_num,
                'page_url': url,
                'viewer_url': full_viewer_url,
                'title': cleaned_title,
                'status': 'success'
            }
        else:
            return {
                'page_num': page_num,
                'page_url': url,
                'viewer_url': None,
                'title': cleaned_title,
                'status': 'no_iframe_found'
            }
            
    except Exception as e:
        return {
            'page_num': page_num,
            'page_url': url,
            'viewer_url': None,
            'title': "",
            'status': f'error: {str(e)}'
        }

def save_to_csv(data, filename, is_first_page=False):
    """将数据保存到CSV文件"""
    df = pd.DataFrame([data])
    
    # 如果是第一页且文件不存在，写入header；否则追加数据
    if is_first_page or not os.path.exists(filename):
        df.to_csv(filename, index=False, mode='w')
    else:
        df.to_csv(filename, index=False, mode='a', header=False)

def main():
    error_count = 0
    current_page = START_PAGE
    
    # 创建或清空输出文件
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    # 当错误计数小于最大允许错误时继续循环
    while error_count < MAX_ERRORS:
        print(f"Processing page {current_page}...")
        
        # 获取当前页面的数据
        page_data = get_pdf_viewer_url(current_page)
        
        # 如果是错误状态(非成功且非无iframe)，增加错误计数
        if page_data['status'] != 'success' and page_data['status'] != 'no_iframe_found':
            error_count += 1
        
        # 立即保存结果到CSV
        save_to_csv(page_data, OUTPUT_FILE, is_first_page=(current_page == START_PAGE))
        
        # 打印当前状态
        if page_data['viewer_url']:
            print(f"Found viewer URL: {page_data['viewer_url']}")
            print(f"Title: {page_data['title']}")
        else:
            print(f"No viewer found or error: {page_data['status']}")
        
        # 移动到下一页
        current_page += 1
        
        # 延迟以防止被封
        time.sleep(REQUEST_DELAY)
    
    print(f"Completed. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()