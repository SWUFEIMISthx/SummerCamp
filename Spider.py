from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# 选择"问询与回复"板块
try:
    inquiry_reply_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-type="4"]'))
    )
    inquiry_reply_button.click()
    # 等待页面加载
    time.sleep(5)
except (TimeoutException, NoSuchElementException) as e:
    print(f"Failed to select '问询与回复' section: {e}")
    driver.quit()
    exit()

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
        all_pdf_links.extend([link['href'] for link in pdf_links])

        if page < total_pages:
            # 使用JavaScript进行分页跳转
            driver.execute_script(f'document.querySelector("ul#jqPaginator li a[data-pi=\'{page}\']").click()')

            # 等待页面加载
            time.sleep(5)

            # 打印当前页面的一部分源代码
            new_page_source = driver.page_source
            print(f"Page {page + 1} source sample: {new_page_source[:500]}")

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Exception on page {page}: {e}")
        break

# 关闭 WebDriver
driver.quit()

# 创建文件夹用于保存下载的 PDF 文件
os.makedirs('pdf_files', exist_ok=True)

# 下载所有 PDF 文件
for link in all_pdf_links:
    pdf_url = link
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