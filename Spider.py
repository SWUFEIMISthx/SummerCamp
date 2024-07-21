import requests
from bs4 import BeautifulSoup
import os

# 目标 URL
url = 'https://listing.szse.cn/disclosure/ipo/index.html'

# 请求网页内容
response = requests.get(url)
response.encoding = 'utf-8'  # 根据网页编码进行设置

# 检查请求是否成功
if response.status_code == 200:
    # 解析 HTML 内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找所有的 a 标签，并过滤出链接中包含 .pdf 的
    pdf_links = soup.find_all('a', href=lambda href: href and '.pdf' in href)

    # 创建一个文件夹用于保存下载的 PDF 文件
    os.makedirs('pdf_files', exist_ok=True)

    # 下载每个 PDF 文件
    for link in pdf_links:
        pdf_url = link['href']
        # 如果链接是相对路径，构造完整的 URL
        if not pdf_url.startswith('http'):
            pdf_url = 'https://www.szse.cn' + pdf_url

        # 获取 PDF 文件名
        pdf_name = os.path.join('pdf_files', os.path.basename(pdf_url))

        # 下载 PDF 文件
        pdf_response = requests.get(pdf_url)
        if pdf_response.status_code == 200:
            with open(pdf_name, 'wb') as pdf_file:
                pdf_file.write(pdf_response.content)
            print(f"Downloaded: {pdf_name}")
        else:
            print(f"Failed to download: {pdf_url}")

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
