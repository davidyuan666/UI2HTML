import requests
from bs4 import BeautifulSoup
import os
import time

def download_glyphicon_examples():
    # 创建保存目录
    if not os.path.exists('glyphicons'):
        os.makedirs('glyphicons')
        os.makedirs('glyphicons/images')
        os.makedirs('glyphicons/code')
    
    # 获取页面内容
    url = 'https://www.runoob.com/bootstrap/bootstrap-glyphicons.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 找到图标表格
    table = soup.find('table')
    if not table:
        print("未找到图标表格")
        return
    
    # 遍历每个图标
    for row in table.find_all('tr')[1:]:  # 跳过表头
        cols = row.find_all('td')
        if len(cols) >= 2:
            icon_class = cols[0].text.strip()
            try_link = cols[1].find('a')['href']
            
            # 获取示例页面
            example_url = f"https://www.runoob.com{try_link}"
            example_response = requests.get(example_url)
            example_soup = BeautifulSoup(example_response.text, 'html.parser')
            
            # 保存HTML代码
            code_block = example_soup.find('pre')
            if code_block:
                with open(f'glyphicons/code/{icon_class}.html', 'w', encoding='utf-8') as f:
                    f.write(code_block.text)
            
            # 保存示例截图（如果有的话）
            example_div = example_soup.find('div', class_='example')
            if example_div:
                # 这里需要使用selenium或其他工具来截图
                pass
            
            print(f"已下载 {icon_class}")
            time.sleep(1)  # 避免请求过快
            
    print("下载完成！")

if __name__ == "__main__":
    download_glyphicon_examples()