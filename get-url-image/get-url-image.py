import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin, urlparse  # 修改导入


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
        
        # 检查路径后缀
        if path.endswith(('.jpg', '.jpeg')):
            if link not in seen:
                seen.add(link)
                jpg_links.append(link)
    return jpg_links

def save_to_csv(links, filename='images.csv'):
    """保存链接到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Image_URL'])
        writer.writerows([[link] for link in links])
    print(f"成功保存{len(links)}个链接到 {filename}")

def main(url):
    html = fetch_webpage(url)
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
