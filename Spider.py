from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests
import os
import time

# 设置 ChromeDriver 路径
chrome_driver_path = 'D:\\Chrome Driver\\ChromeDriver_installpackage\\chromedriver-win64\\chromedriver.exe'
service = Service(chrome_driver_path)

# 设置 Chrome 选项
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

# 启动 WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# 打开目标网页
url = 'https://listing.szse.cn/disclosure/ipo/index.html'
driver.get(url)

# 等待几秒钟以确保所有内容加载完毕
time.sleep(5)

# 获取总页数
total_pages = 537  # 根据你的截图中的页码数

# 初始化用于存储所有PDF链接的列表
all_pdf_links = []

# 循环遍历每一页
for page in range(1, total_pages + 1):
    try:
        # 获取当前页面源代码
        page_source = driver.page_source

        # 解析 HTML
        soup = BeautifulSoup(page_source, 'html.parser')
        pdf_links = soup.find_all('a', href=lambda href: href and '.pdf' in href)

        # 将当前页面的PDF链接添加到总列表中
        all_pdf_links.extend(pdf_links)

        if page < total_pages:
            # 找到页码输入框并输入页码
            page_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.pagination-con input[type="text"]'))
            )
            page_input.clear()
            page_input.send_keys(str(page + 1))

            # 找到“跳转”按钮并点击
            jump_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.pagination-con button'))
            )
            jump_button.click()

            # 等待页面加载
            time.sleep(10)
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Exception on page {page}: {e}")
        break

# 关闭 WebDriver
driver.quit()

# 创建文件夹用于保存下载的 PDF 文件
os.makedirs('pdf_files', exist_ok=True)

# 下载所有 PDF 文件
for link in all_pdf_links:
    pdf_url = link['href']
    if not pdf_url.startswith('http'):
        pdf_url = 'https://www.szse.cn' + pdf_url

    pdf_name = os.path.join('pdf_files', os.path.basename(pdf_url))
    pdf_response = requests.get(pdf_url)
    if pdf_response.status_code == 200:
        with open(pdf_name, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Downloaded: {pdf_name}")
    else:
        print(f"Failed to download: {pdf_url}")