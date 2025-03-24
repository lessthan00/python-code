import requests
from bs4 import BeautifulSoup
import csv
import os
from urllib.parse import urljoin, urlparse
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def fetch_webpage_with_selenium(url):
    """使用Selenium获取动态加载的网页内容"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # 等待页面加载
    html = driver.page_source
    driver.quit()
    return html


def fetch_webpage(url):
    """获取网页内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"错误：无法获取网页内容 - {e}")
        return None

def extract_image_links(html, base_url):
    """解析HTML并提取所有图片链接"""
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img')
    links = []
    for img in img_tags:
        src = img.attrs.get('src') or img.attrs.get('data-src', '')
        if src:
            absolute_url = urljoin(base_url, src)
            links.append(absolute_url)
    return links

def filter_jpg_links(links):
    """改进版过滤逻辑：精确识别含参数的JPG链接"""
    seen = set()
    jpg_links = []
    for link in links:
        # 解析URL路径部分
        parsed = urlparse(link)
        path = parsed.path.lower()
        
        # 使用正则表达式匹配更多可能的JPG链接
        if re.search(r'\.jpe?g($|\?)', path):
            if link not in seen:
                seen.add(link)
                jpg_links.append(link)
    return jpg_links

def save_to_csv(links, filename='images.csv'):
    """保存链接到CSV文件，如果文件存在则追加，否则创建新文件"""
    # 检查文件是否存在
    file_exists = os.path.isfile(filename)

    with open(filename, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # 如果文件不存在，写入表头
        if not file_exists:
            writer.writerow(['Image_URL'])
        
        # 写入链接数据
        writer.writerows([[link] for link in links])
    
    print(f"成功保存{len(links)}个链接到 {filename}")

def main(url):
    html = fetch_webpage(url) # 静态加载
    # html = fetch_webpage_with_selenium(url) # 动态加载
    if not html:
        return
    
    all_links = extract_image_links(html, url)
    jpg_links = filter_jpg_links(all_links)
    
    if jpg_links:
        save_to_csv(jpg_links)
    else:
        print("未找到JPG格式的图片链接")

if __name__ == "__main__":
    target_url = input("请输入要抓取的网页URL：")
    main(target_url)