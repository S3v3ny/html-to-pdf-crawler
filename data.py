import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from xhtml2pdf import pisa
TARGET_URL = "https://webpath.med.utah.edu" #/HISTHTML/ANATOMY/VHM1080R.html
DELAY = 0  # 请求延迟（秒）

#下载图片到本地，返回本地路径
def download_image(img_url, save_dir):
    try:
        os.makedirs(save_dir, exist_ok=True)
        parsed_img = urlparse(img_url)
        # 处理图片文件名（解码URL中的特殊字符）
        img_filename = os.path.basename(unquote(parsed_img.path))
        if not img_filename:  # 无文件名时用哈希生成唯一名称
            img_filename = f"img_{hash(img_url)}.jpg"
        local_img_path = os.path.join(save_dir, img_filename)
        #print(img_filename)

        if os.path.exists(local_img_path):
            return local_img_path
            
        #防反爬
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Referer": TARGET_URL 
        }
        if(img_filename!='back.gif')and(img_filename!='fwd.gif')and(img_filename!='help.gif')and(img_filename!='arrowred.gif'):
            response = requests.get(img_url, headers=headers, timeout=10, stream=True)
            if (response.status_code == 200):
                with open(local_img_path, "wb") as f:
                    f.write(response.content)  # 二进制保存（支持GIF等格式）
                print(f"已下载图片：{local_img_path}")
                return local_img_path
            else:
                print(f"图片下载失败（状态码：{response.status_code}）：{img_url}")
                return None
    except Exception as e:
        print(f"图片下载错误：{str(e)}")
        return None

#提取目标内容
def extract_chapter_content(target_url):
    print(f"开始爬取目标章节：{target_url}")
    # 存储当前章节的内容
    chapter_data = {
    "title": "",
    "text": "",
    "images": []  
    }
    try:
        #发送请求获取页面
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        }
        response = requests.get(target_url, headers=headers, timeout=10)
        response.encoding = "utf-8"  # 根据网站编码调整（通常是utf-8）
        html_content = response.text
        
        #解析HTML提取内容
        soup = BeautifulSoup(html_content, "html.parser")
        #print(soup)
        
        # 提取章节标题
        title_tag = soup.find("title") or soup.find("title")
        chapter_data["title"] = title_tag.get_text(strip=True) if title_tag else "未知章节"
        
        # 提取正文文字（过滤无关内容，保留段落、列表等）
        content_tags = soup.find_all(["p", "div", "li", "h3","tr","td"]) 
        text_parts = []
        for tag in content_tags:
            # 过滤导航、广告等无关标签（根据网站class/id调整）
            if "nav" in tag.get("class", []) or "menu" in tag.get("class", []) or "ad" in tag.get("class", []):
                continue
            text = tag.get_text(strip=True)
            #print(text)
            if text:
                text_parts.append(text)
        chapter_data["text"] = "\n\n".join(text_parts)  # 段落间换行
        
        # 3. 提取并下载图片
        img_save_dir = "chapter_images"  # 图片保存目录（当前文件夹下）
        for img_tag in soup.find_all("img"):
            img_src = img_tag.get("src") or img_tag.get("data-src")
            if img_src:
                # 转换为绝对URL
                absolute_img_url = urljoin(TARGET_URL, img_src)
                # 只下载当前网站的图片
                if urlparse(absolute_img_url).netloc == urlparse(TARGET_URL).netloc:
                    local_img_path = download_image(absolute_img_url, img_save_dir)
                    if local_img_path:
                        chapter_data["images"].append(local_img_path)
        
        print("章节内容提取完成")
        return chapter_data
    except Exception as e:
        print(f"爬取失败：{str(e)}")


def generate_pdf(pdf_name,chapter_data):
    """将提取的内容生成PDF"""
    if not chapter_data["title"]:
        print("无内容可生成PDF")
        return
    #print(chapter_data["text"])
    # 1. 生成临时HTML（用于转换PDF，保留排版）
    temp_html = "temp_chapter.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write("<html><head>")
        f.write("<meta charset='utf-8'>")
        f.write(f"<title>{chapter_data['title']}</title>")
        f.write("</head><body>")
        # 标题
        f.write(f"<h1 style='text-align:center;'>{chapter_data['title']}</h1>")
        # 正文
        f.write(f"<div style='font-size:12pt; line-height:1.6;'>")
        # 文字内容（换行转为HTML换行）
        f.write(chapter_data["text"].replace("\n\n", "<p></p>"))
        f.write("</div>")
        # 图片（居中显示，限制最大宽度）
        for img_path in chapter_data["images"]:
            if os.path.exists(img_path):
                f.write(f"<p style='text-align:center;'>")
                f.write(f"<img src='{img_path}' style='max-width:90%;'>")
                f.write(f"</p>")
        f.write("</body></html>")
    
    # 2. 转换HTML为PDF
    try:
        with open(temp_html,"r") as f:
            htmlstr=f.read()
            with open(pdf_name, "wb") as f:
                pisa.CreatePDF(htmlstr, dest=f)
        print(f"PDF生成成功：{os.path.abspath(pdf_name)}")
    except Exception as e:
        print(f"PDF生成失败：{str(e)}")
    #finally:
        # 删除临时HTML
        if os.path.exists(temp_html):
             os.remove(temp_html)


if __name__ == "__main__":
    # 步骤1：爬取并提取目标子章节内容
    for i in range(199,261):
        target_url=TARGET_URL+"/HISTHTML/ANATOMY/VHM%.3d0R.html"%i  #//HISTHTML/ANATOMY/VHM1080A.html
        pdf_name="./output/vhm%.3d.pdf"%i
        chapter_data=extract_chapter_content(target_url)
        # 步骤2：生成PDF
        generate_pdf(pdf_name,chapter_data)
        print(target_url)
    print("操作完成")