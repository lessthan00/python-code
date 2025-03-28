# python download GB stand pdf from yiqifuwu

https://www.yiqifuwu.com/standard/x.html 找到 pdf 的url
跳转后的url 类似于https://www.yiqifuwu.com/statics/js/pdf/web/viewer.html?file=/uploadfile/file/20250326/1742978958889379.pdf
还要找到类似<title> GB/T 1094.1-2013 电力变压器 第1部分：总则-宜器服务网 </title>, 需要去除-宜器服务网
x从1到失败30次为准
网站有反爬虫机制，需要设置请求间隔时间，防止被封
依赖和代码,使用python实现

## 实现 环境隔离

sudo apt update
sudo apt install python3 python3-venv
python3 -m venv venv # 创建名为 venv 的虚拟环境目录
source venv/bin/activate # 激活虚拟环境

## 依赖
pip3 install requests beautifulsoup4 pandas
pip3 install requests fake-useragent

## 运行
python3 download_form_yiqifuwu.py # 运行脚本
python3 download_form_csv.py yiqifuwu_pdf_viewer_urls.csv #替换为实际保存url的csv文件名称

## 保存依赖
pip3 freeze > requirements.txt # 管理依赖
deactivate # 虚拟环境

## 再次运行时, 使用 requirements.txt 安装

pip install -r requirements.txt

deactivate  # 确保退出当前虚拟环境
rm -rf venv  # 删除旧的虚拟环境
python3 -m venv venv  # 创建新的虚拟环境
source venv/bin/activate  # 激活新的虚拟环境

## 如果需要在windows上运行

```shell

# 删除旧的 Linux venv（如果有）
rm -r venv  

# 创建新的 Windows 虚拟环境
python -m venv venv  

# 激活虚拟环境
.\venv\Scripts\activate  

# 安装依赖（如果有 requirements.txt）
pip install -r requirements.txt  
python download_form_csv.py yiqifuwu_pdf_viewer_urls.csv
```