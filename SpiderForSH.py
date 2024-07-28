from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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
url = 'https://listing.sse.com.cn/disclosure/'
driver.get(url)

# 等待几秒钟以确保所有内容加载完毕
time.sleep(5)

# 调试信息：打印页面源代码
print(driver.page_source)

# 选择问询与回复板块
try:
    disclosure_type = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "DisclosureType"))
    )
    print("Disclosure type found")

    # 尝试使用不同的选择器来选择“问询与回复”标签
    inquiry_response_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//li[text()="问询与回复"]'))
    )
    print("Inquiry and response tab found")
    driver.execute_script("arguments[0].scrollIntoView(true);", inquiry_response_tab)
    inquiry_response_tab.click()

    # 等待页面加载
    time.sleep(5)
except TimeoutException as e:
    print("Failed to locate or click the inquiry and response tab:", e)
    driver.quit()
    exit()

# 获取总页数
total_pages = 632

# 根据你的截图中的页码数

# 初始化用于存储所有PDF链接的列表
all_pdf_links = []

# 断点续传机制
start_page = 1
if os.path.exists('last_page.txt'):
    with open('last_page.txt', 'r') as f:
        start_page = int(f.read().strip())

# 循环遍历每一页
for page in range(start_page, total_pages + 1):
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
            next_button = driver.find_element(By.ID, "dataList_container_next")
            driver.execute_script("arguments[0].click();", next_button)

            # 等待页面加载
            time.sleep(5)

            # 打印当前页面的一部分源代码
            new_page_source = driver.page_source
            print(f"Page {page + 1} source sample: {new_page_source[:500]}")

        # 保存当前页码到文件
        with open('last_page.txt', 'w') as f:
            f.write(str(page))

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Exception on page {page}: {e}")
        break

# 关闭 WebDriver
driver.quit()

# 创建文件夹用于保存下载的 PDF 文件
os.makedirs('pdf_files_SH', exist_ok=True)

# 下载所有 PDF 文件
for link in all_pdf_links:
    pdf_url = link
    if not pdf_url.startswith('http'):
        pdf_url = 'https://www.sse.com.cn' + pdf_url

    pdf_name = os.path.join('pdf_files_SH', os.path.basename(pdf_url))
    pdf_response = requests.get(pdf_url, timeout=10)
    if pdf_response.status_code == 200:
        with open(pdf_name, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Downloaded: {pdf_name}")
    else:
        print(f"Failed to download: {pdf_url}")
