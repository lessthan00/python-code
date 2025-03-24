# python 网页图片元素获取

输入网页url, 返回网页中的图片的url列表,输出为csv文件

## 实现 环境隔离

sudo apt update
sudo apt install python3 python3-venv
python3 -m venv venv # 创建名为 venv 的虚拟环境目录
source venv/bin/activate # 激活虚拟环境
pip3 install urllib3==1.26.6 
pip3 install requests beautifulsoup4
python3 get-url-image.py # 运行脚本
pip3 freeze > requirements.txt # 管理依赖
deactivate # 虚拟环境

## 再次运行时, 使用 requirements.txt 安装

pip install -r requirements.txt